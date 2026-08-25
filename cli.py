#!/usr/bin/env python3
"""
Command-line interface for the Wells Score Calculator.

Supports interactive scoring for DVT and PE, plus the Revised Geneva Score.
Stdlib only — no external dependencies.

Usage:
    python cli.py dvt          # Interactive DVT scoring
    python cli.py pe           # Interactive PE scoring
    python cli.py geneva       # Interactive Revised Geneva scoring
    python cli.py dvt --json '{"active_cancer": true, "previous_dvt": true}'
    python cli.py pe --json '{"clinical_dvt_signs": true, "heart_rate_100": true}'
    python cli.py criteria     # List all criteria for all scores
"""

import argparse
import json
import sys

from wells import (
    calculate_dvt,
    calculate_pe,
    calculate_geneva,
    list_dvt_criteria,
    list_pe_criteria,
    list_geneva_criteria,
    DVT_CRITERIA,
    PE_CRITERIA,
    GENEVA_CRITERIA,
)


def _prompt_criteria(criteria_list, label):
    """Interactively prompt the user for each criterion."""
    print(f"\n{'=' * 60}")
    print(f"  Wells Score for {label}")
    print(f"{'=' * 60}")
    print("Answer yes/no for each criterion:\n")

    responses = {}
    for key, points, description in criteria_list:
        if points < 0:
            prompt = f"  {description} [{points:+g} pts] (yes/no): "
        else:
            prompt = f"  {description} [+{points:g} pts] (yes/no): "

        while True:
            answer = input(prompt).strip().lower()
            if answer in ("yes", "y", "1"):
                responses[key] = True
                break
            elif answer in ("no", "n", "0"):
                responses[key] = False
                break
            else:
                print("    Please enter 'yes' or 'no'.")

    return responses


def _print_result(result, score_type):
    """Pretty-print a scoring result."""
    print(f"\n{'=' * 60}")
    print(f"  {score_type} RESULT")
    print(f"{'=' * 60}")
    print(f"\n  Score: {result['score']:.1f}")

    if result.get("criteria_met"):
        print(f"\n  Criteria present:")
        for c in result["criteria_met"]:
            pts = c["points"]
            sign = "+" if pts >= 0 else ""
            print(f"    {sign}{pts:g}  {c['description']}")
    else:
        print("\n  No criteria present.")

    if "two_tier" in result:
        t = result["two_tier"]
        print(f"\n  Two-tier interpretation:")
        print(f"    Category:   {t['category']}")
        print(f"    Prevalence: ~{t['prevalence_pct']}%")
        print(f"    Action:     {t['recommendation']}")

    if "three_tier" in result:
        t = result["three_tier"]
        print(f"\n  Three-tier interpretation:")
        print(f"    Category:   {t['category']}")
        print(f"    Prevalence: ~{t['prevalence_pct']}%")
        print(f"    Action:     {t['recommendation']}")

    if "ddimer_guidance" in result:
        print(f"\n  D-dimer guidance:")
        print(f"    {result['ddimer_guidance']}")

    print(f"\n{'=' * 60}")
    print("  DISCLAIMER: Clinical decision support only.")
    print("  Always correlate with clinical judgment and confirmatory testing.")
    print(f"{'=' * 60}\n")


def cmd_dvt(args):
    """Run DVT scoring."""
    if args.json:
        criteria = json.loads(args.json)
    else:
        criteria = _prompt_criteria(DVT_CRITERIA, "DVT (Deep Vein Thrombosis)")

    result = calculate_dvt(criteria)
    _print_result(result, "WELLS DVT")
    return 0


def cmd_pe(args):
    """Run PE scoring."""
    if args.json:
        criteria = json.loads(args.json)
    else:
        criteria = _prompt_criteria(PE_CRITERIA, "PE (Pulmonary Embolism)")

    result = calculate_pe(criteria)
    _print_result(result, "WELLS PE")
    return 0


def cmd_geneva(args):
    """Run Revised Geneva scoring."""
    if args.json:
        criteria = json.loads(args.json)
    else:
        criteria = _prompt_criteria(GENEVA_CRITERIA, "Revised Geneva (PE)")

    result = calculate_geneva(criteria)
    _print_result(result, "REVISED GENEVA PE")
    return 0


def cmd_criteria(args):
    """List all criteria for all scoring systems."""
    print("\n" + "=" * 60)
    print("  WELLS SCORE CRITERIA")
    print("=" * 60)

    print("\n  --- Wells DVT Criteria (range: -2 to 9) ---")
    for c in list_dvt_criteria():
        pts = c["points"]
        sign = "+" if pts >= 0 else ""
        print(f"    {sign}{pts:g}  {c['key']:25s}  {c['description']}")

    print("\n  --- Wells PE Criteria (range: 0 to 12.5) ---")
    for c in list_pe_criteria():
        print(f"    +{c['points']:g}  {c['key']:25s}  {c['description']}")

    print("\n  --- Revised Geneva Criteria (range: 0 to 21) ---")
    for c in list_geneva_criteria():
        print(f"    +{c['points']:g}  {c['key']:25s}  {c['description']}")

    print()
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="wells",
        description="Wells Score Calculator for DVT and PE (clinical decision support)",
    )
    sub = parser.add_subparsers(dest="command")

    # DVT
    p_dvt = sub.add_parser("dvt", help="Calculate Wells Score for DVT")
    p_dvt.add_argument("--json", type=str, default=None,
                       help='JSON string of criteria, e.g. \'{"active_cancer": true}\'')

    # PE
    p_pe = sub.add_parser("pe", help="Calculate Wells Score for PE")
    p_pe.add_argument("--json", type=str, default=None,
                      help='JSON string of criteria, e.g. \'{"heart_rate_100": true}\'')

    # Geneva
    p_geneva = sub.add_parser("geneva", help="Calculate Revised Geneva Score for PE")
    p_geneva.add_argument("--json", type=str, default=None,
                          help='JSON string of criteria')

    # Criteria listing
    sub.add_parser("criteria", help="List all criteria for all scoring systems")

    args = parser.parse_args(argv)

    if args.command == "dvt":
        return cmd_dvt(args)
    elif args.command == "pe":
        return cmd_pe(args)
    elif args.command == "geneva":
        return cmd_geneva(args)
    elif args.command == "criteria":
        return cmd_criteria(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
