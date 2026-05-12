from __future__ import annotations
import argparse, importlib, json, sys
from pathlib import Path
from .validate import validate, load_rubric, validate_rubric
from .diff import diff
from .lint import lint
from .conformance import run_conformance

ADAPTERS = {"inspect_ai", "promptfoo", "deepeval", "langsmith", "evalkit", "rubric_spec"}

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="rubric-spec")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("validate"); p.add_argument("path")
    p = sub.add_parser("diff"); p.add_argument("old"); p.add_argument("new")
    p = sub.add_parser("lint"); p.add_argument("path")
    p = sub.add_parser("convert"); p.add_argument("--from", dest="source", required=True); p.add_argument("--to", dest="target", required=True); p.add_argument("path", nargs="?")
    p = sub.add_parser("conformance"); p.add_argument("path", nargs="?", default=str(Path(__file__).resolve().parents[2] / "examples" / "minimal_rubric.json"))
    args = parser.parse_args(argv)
    if args.cmd == "validate":
        result = validate(args.path); print(json.dumps(result.to_dict(), indent=2)); return 0 if result.ok else 1
    if args.cmd == "diff": print(json.dumps(diff(args.old, args.new).to_dict(), indent=2)); return 0
    if args.cmd == "lint":
        findings = [f.__dict__ for f in lint(args.path)]; print(json.dumps({"findings": findings, "error_count": sum(f["severity"] == "error" for f in findings)}, indent=2)); return 0 if not any(f["severity"] == "error" for f in findings) else 1
    if args.cmd == "convert":
        raw = open(args.path, encoding="utf-8").read() if args.path else sys.stdin.read(); data = json.loads(raw)
        spec = data if args.source == "rubric_spec" else importlib.import_module(f"rubric_spec.adapters.{args.source}").to_spec(data)
        out = spec if args.target == "rubric_spec" else importlib.import_module(f"rubric_spec.adapters.{args.target}").from_spec(spec)
        validation = validate_rubric(spec)
        if not validation.ok: print(json.dumps(validation.to_dict(), indent=2), file=sys.stderr); return 1
        print(json.dumps(out, indent=2, sort_keys=True)); return 0
    if args.cmd == "conformance":
        report = run_conformance(args.path)
        print(json.dumps(report.to_dict(), indent=2)); return 0 if report.ok else 1
    return 2
if __name__ == "__main__": raise SystemExit(main())
