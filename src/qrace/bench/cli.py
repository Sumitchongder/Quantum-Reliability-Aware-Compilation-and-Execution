"""Command-line interface: ``qrace-bench {build,verify,summary,list}``.

Examples::

    qrace-bench build --spec pilot --out data/bench/pilot
    qrace-bench verify data/bench/pilot --max-qubits 10
    qrace-bench summary data/bench/pilot
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Sequence

from .suite import SUITE_SPECS, build_suite, load_suite, save_suite, summarize, verify_suite


def _markdown_table(rows: list[dict]) -> str:
    if not rows:
        return "(empty)"
    keys = list(rows[0])
    lines = ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
    lines += ["| " + " | ".join(str(r[k]) for k in keys) + " |" for r in rows]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qrace-bench", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="build a named suite and save it")
    p_build.add_argument("--spec", choices=sorted(SUITE_SPECS), default="pilot")
    p_build.add_argument("--out", required=True, help="output directory")
    p_build.add_argument("--families", nargs="*", help="subset of families, e.g. F1 F4")

    p_verify = sub.add_parser("verify", help="re-check ideal values against a state vector")
    p_verify.add_argument("path")
    p_verify.add_argument("--max-qubits", type=int, default=10)

    p_sum = sub.add_parser("summary", help="print a per-family summary table")
    p_sum.add_argument("path")

    sub.add_parser("list", help="list the available suite specifications")

    args = parser.parse_args(argv)

    if args.command == "list":
        for name, spec in SUITE_SPECS.items():
            print(f"{name:6s} {sum(spec.per_family.values()):4d} instances  {spec.per_family}")
        return 0

    if args.command == "build":
        spec = SUITE_SPECS[args.spec]
        t0 = time.perf_counter()
        instances = build_suite(spec, families=args.families)
        manifest = save_suite(instances, args.out, spec=spec)
        print(f"built {len(instances)} instances in {time.perf_counter() - t0:.1f} s -> {manifest}")
        print(_markdown_table(summarize(instances)))
        return 0

    instances = load_suite(args.path)
    if args.command == "summary":
        print(_markdown_table(summarize(instances)))
        return 0
    if args.command == "verify":
        report = verify_suite(instances, max_qubits=args.max_qubits)
        print(json.dumps(report, indent=2))
        return 0 if report["passed"] else 1
    return 2  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
