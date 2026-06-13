#!/usr/bin/env python3
"""
cli.py — Lighthouse CLI entry point.

Provides all fleet coordination commands:
  scan       Scan fleet repos and build catalog
  beachcomb  Run beachcomb sweep for new bottles/PRs
  infer      Infer agent context from commits
  status     Show fleet health summary
  bottle     Drop/read/list bottles
  onboard    Generate skeleton for a new agent vessel
  config     View/edit lighthouse configuration
"""

import argparse
import json
import os
import sys
from pathlib import Path

from .utils.github import GitHubClient
from .utils.config import LighthouseConfig


def cmd_scan(args):
    """Scan fleet repos and display catalog."""
    client = GitHubClient(org=args.org)
    from .discovery.fleet_scan import FleetScanner

    scanner = FleetScanner(client)
    print("Scanning fleet repos...")
    catalog = scanner.build_catalog()

    print(f"\nFound {catalog['total_repos']} repos")
    print(f"\nBy Type:")
    for rtype, count in sorted(catalog["by_type"].items(), key=lambda x: -x[1]):
        print(f"  {rtype}: {count}")

    print(f"\nBy Language:")
    for lang, count in sorted(catalog["by_language"].items(), key=lambda x: -x[1])[:10]:
        print(f"  {lang}: {count}")

    print(f"\nHealth Distribution:")
    for band, count in catalog["by_health"].items():
        print(f"  {band}: {count}")

    if args.json:
        print("\n--- JSON ---")
        print(json.dumps(catalog, indent=2))

    if args.output:
        report = scanner.generate_health_report(catalog)
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"\nHealth report saved to {args.output}")


def cmd_beachcomb(args):
    """Run beachcomb sweep for new forks/PRs/bottles."""
    client = GitHubClient(org=args.org)
    from .beachcomb.scanner import BeachcombScanner

    scanner = BeachcombScanner(client)
    print("Running beachcomb sweep...")

    if args.dry_run:
        print("(dry run -- no state will be saved)")

    results = scanner.run_full_scan(repo_limit=args.limit)

    print(f"\nResults:")
    print(f"  New forks: {len(results['new_forks'])}")
    print(f"  New PRs: {len(results['new_prs'])}")
    print(f"  New external bottles: {len(results['new_bottles'])}")
    print(f"  Totals: {results['totals']}")

    if results["has_new_activity"]:
        print("\nNEW ACTIVITY DETECTED!")
        report = scanner.generate_report(results)
        print(report)

    if args.json:
        print("\n--- JSON ---")
        print(json.dumps(results, indent=2))

    if args.output:
        report = scanner.generate_report(results)
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"\nReport saved to {args.output}")


def cmd_infer(args):
    """Infer agent context from commits."""
    client = GitHubClient(org=args.org)
    from .context.infer import ContextInferrer

    inferrer = ContextInferrer(client)
    owner = args.owner or args.org
    vessel = args.vessel or f"{owner}-vessel"

    print(f"Inferring context for {owner}...")
    repos_data = client.get(f"/users/{owner}/repos", {
        "sort": "updated", "per_page": "30",
    })
    if not isinstance(repos_data, list):
        print(f"Could not fetch repos for {owner}")
        sys.exit(1)

    active_repos = [r["name"] for r in repos_data[:20]]
    print(f"Active repos: {', '.join(active_repos[:10])}")

    expertise = inferrer.infer_expertise(owner, active_repos)
    report = inferrer.generate_synergy_report(owner, expertise, {})
    print(report)

    if args.json:
        print("\n--- JSON ---")
        print(json.dumps(expertise, indent=2))


def cmd_status(args):
    """Show fleet health summary."""
    client = GitHubClient(org=args.org)
    from .discovery.fleet_scan import FleetScanner

    scanner = FleetScanner(client)
    catalog = scanner.build_catalog()

    print(f"# Lighthouse Fleet Status")
    print(f"Org: {catalog['org']} | Repos: {catalog['total_repos']}")
    print(f"Generated: {catalog['generated_at'][:19]}\n")

    # Health breakdown
    h = catalog["by_health"]
    total = catalog["total_repos"]
    fresh_pct = (h["fresh"] / total * 100) if total else 0
    print(f"Fleet Health: {fresh_pct:.1f}% fresh")
    print(f"  Fresh: {h['fresh']} | Aging: {h['aging']} | Stale: {h['stale']} | Dead: {h['dead']}")

    print(f"\nTop repos:")
    for repo in catalog["repos"][:10]:
        print(f"  {repo['name']:40} health={repo['health']:.2f} type={repo['type']}")


def cmd_bottle(args):
    """Drop/read/list bottles."""
    from .git.bottle import BottleManager

    bottle_dir = getattr(args, "bottle_dir", None)
    mgr = BottleManager(bottle_dir=bottle_dir)

    if args.action == "list":
        target = args.recipient
        bottles = mgr.list_bottles(target=target)
        if not bottles:
            print(f"No bottles found" + (f" for {target}" if target else ""))
            return
        for b in bottles:
            print(f"  [{b.get('date', '??')[:16]}] {b.get('from', '??')} -> {b.get('to', '??')}: {b.get('subject', '??')}")

    elif args.action == "drop":
        if not args.recipient:
            print("Error: --recipient required for drop")
            sys.exit(1)
        path = mgr.drop(
            recipient=args.recipient,
            subject=args.subject or "Status Update",
            content=args.content or "No content",
            sender=args.sender or "Lighthouse",
        )
        print(f"Bottle dropped: {path}")

    elif args.action == "search":
        if not args.subject:
            print("Error: --subject required for search")
            sys.exit(1)
        results = mgr.search_bottles(args.subject)
        for r in results:
            print(f"  {r['filename']}: {r.get('subject', '')}")

    elif args.action == "dirs":
        print("Bottle directories:")
        for d in mgr.directories:
            print(f"  {d}")


def cmd_onboard(args):
    """Generate a skeleton for a new agent vessel."""
    from .git.onboard import Onboarder

    client = GitHubClient(org=args.org)
    onboarder = Onboarder(client)

    name = args.name
    if not name:
        print("Error: --name required for onboard")
        sys.exit(1)

    agent_type = args.type or "vessel"
    specialization = args.specialization or ""
    emoji = args.emoji or "?"
    org = args.target_org or args.org

    print(f"Generating vessel skeleton for {name}...")
    result = onboarder.generate_skeleton(
        name=name,
        agent_type=agent_type,
        specialization=specialization,
        emoji=emoji,
        org=org,
        output_dir=args.output_dir,
    )

    print(f"\nSkeleton generated at: {result['path']}")
    print(f"Files created: {len(result['files'])}")
    for f in sorted(result["files"]):
        print(f"  {f}")


def cmd_config(args):
    """View/edit lighthouse configuration."""
    config = LighthouseConfig()

    if args.action == "show":
        print(f"Config path: {config.config_path}")
        print(f"Org: {config.org}")
        print(f"Scan interval: {config.scan_interval} min")
        print(f"Expected agents: {', '.join(config.expected_agents)}")
        print(f"Heartbeat timeout: {config.heartbeat_timeout_hours}h")
        print(f"Beachcomb action: {config.beachcomb_action}")
        print(f"State DB: {config.state_db_path}")

    elif args.action == "get":
        value = config.get(args.key)
        print(f"{args.key} = {value}")

    elif args.action == "set":
        config.set(args.key, args.value)
        print(f"Set {args.key} = {args.value}")
        print("Note: save() not called -- changes are in-memory only")


def main():
    parser = argparse.ArgumentParser(
        prog="lighthouse",
        description="Lighthouse -- Fleet coordination runtime for the Cocapn fleet",
    )
    parser.add_argument("--org", default=None, help="GitHub org (default: from config)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan fleet repos")
    p_scan.add_argument("--json", action="store_true", help="Output JSON")
    p_scan.add_argument("--output", "-o", help="Save report to file")
    p_scan.set_defaults(func=cmd_scan)

    # beachcomb
    p_bc = subparsers.add_parser("beachcomb", help="Run beachcomb sweep")
    p_bc.add_argument("--dry-run", action="store_true", help="Scan without saving state")
    p_bc.add_argument("--limit", type=int, default=30, help="Max repos to scan")
    p_bc.add_argument("--json", action="store_true", help="Output JSON")
    p_bc.add_argument("--output", "-o", help="Save report to file")
    p_bc.set_defaults(func=cmd_beachcomb)

    # infer
    p_inf = subparsers.add_parser("infer", help="Infer agent context")
    p_inf.add_argument("owner", nargs="?", help="GitHub user to analyze")
    p_inf.add_argument("--vessel", help="Vessel repo name")
    p_inf.add_argument("--json", action="store_true", help="Output JSON")
    p_inf.set_defaults(func=cmd_infer)

    # status
    p_stat = subparsers.add_parser("status", help="Show fleet health")
    p_stat.set_defaults(func=cmd_status)

    # bottle
    p_bot = subparsers.add_parser("bottle", help="Manage bottles")
    p_bot.add_argument("action", choices=["list", "drop", "search", "dirs"])
    p_bot.add_argument("--recipient", "-r", help="Target agent")
    p_bot.add_argument("--subject", "-s", help="Bottle subject")
    p_bot.add_argument("--content", "-c", help="Bottle content")
    p_bot.add_argument("--sender", help="Sender name")
    p_bot.add_argument("--bottle-dir", help="Custom bottle directory")
    p_bot.set_defaults(func=cmd_bottle)

    # onboard
    p_onb = subparsers.add_parser("onboard", help="Generate agent vessel skeleton")
    p_onb.add_argument("--name", required=True, help="Agent name")
    p_onb.add_argument("--type", choices=["vessel", "scout", "tool"], default="vessel")
    p_onb.add_argument("--specialization", help="Agent specialization")
    p_onb.add_argument("--emoji", default="?", help="Agent emoji")
    p_onb.add_argument("--target-org", help="Target GitHub org")
    p_onb.add_argument("--output-dir", help="Output directory")
    p_onb.set_defaults(func=cmd_onboard)

    # config
    p_cfg = subparsers.add_parser("config", help="View/edit configuration")
    p_cfg.add_argument("action", choices=["show", "get", "set"], default="show", nargs="?")
    p_cfg.add_argument("key", nargs="?", help="Config key (for get/set)")
    p_cfg.add_argument("value", nargs="?", help="Config value (for set)")
    p_cfg.set_defaults(func=cmd_config)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
