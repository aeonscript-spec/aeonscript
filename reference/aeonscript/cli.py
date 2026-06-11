"""Command-line interface for the AeonScript reference codec.

Installed as the `aeonscript` script via pyproject.toml [project.scripts].

Subcommands:
    encode INPUT [-o OUTPUT.fasta] [-t MIME] [--id ID]
    decode FASTA [-o OUTPUT]
    inspect FASTA
    validate VECTORS.json

Run `aeonscript --help` for full usage.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import __spec_version__, __version__
from .decoder import decode_oligos
from .encoder import encode_bytes, encode_file


# ---------------------------------------------------------------------------
# FASTA helpers
# ---------------------------------------------------------------------------


def _write_fasta(oligos: list[str], path: Path, block_id: str) -> None:
    with path.open("w", encoding="utf-8") as f:
        for i, oligo in enumerate(oligos):
            f.write(f">{block_id}-oligo-{i:05d}\n{oligo}\n")


def _read_fasta(path: Path) -> list[str]:
    oligos: list[str] = []
    current: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current:
                    oligos.append("".join(current))
                    current = []
            else:
                current.append(line)
        if current:
            oligos.append("".join(current))
    return oligos


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def cmd_encode(args: argparse.Namespace) -> int:
    in_path = Path(args.input)
    if not in_path.exists():
        print(f"error: input file not found: {in_path}", file=sys.stderr)
        return 1
    out_path = Path(args.output) if args.output else in_path.with_suffix(".oligos.fasta")
    block_id = args.id or in_path.name
    mime = args.mime_type

    oligos = encode_file(
        in_path,
        mime_type=mime,
        block_id=block_id,
    )
    _write_fasta(oligos, out_path, block_id)
    total_bases = sum(len(o) for o in oligos)
    payload_size = in_path.stat().st_size
    density = payload_size * 8 / total_bases if total_bases else 0
    print(
        f"✓ encoded {payload_size} bytes → {len(oligos)} oligos "
        f"({total_bases} bases, {density:.3f} bits/base)"
    )
    print(f"  output: {out_path}")
    return 0


def cmd_decode(args: argparse.Namespace) -> int:
    fasta_path = Path(args.fasta)
    if not fasta_path.exists():
        print(f"error: FASTA not found: {fasta_path}", file=sys.stderr)
        return 1
    oligos = _read_fasta(fasta_path)
    if not oligos:
        print(f"error: no oligos found in {fasta_path}", file=sys.stderr)
        return 1

    out_path = (
        Path(args.output)
        if args.output
        else fasta_path.with_suffix(".decoded.bin")
    )
    payload, meta = decode_oligos(oligos, return_metadata=True)
    out_path.write_bytes(payload)
    print(f"✓ decoded {len(payload)} bytes (errors corrected: {meta['errors_corrected']})")
    print(f"  type: {meta['tag'].get('TYPE', '<missing>')}")
    print(f"  id:   {meta['tag'].get('ID', '<missing>')}")
    print(f"  output: {out_path}")
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    fasta_path = Path(args.fasta)
    oligos = _read_fasta(fasta_path)
    if not oligos:
        print(f"error: no oligos found in {fasta_path}", file=sys.stderr)
        return 1

    _, meta = decode_oligos(oligos, return_metadata=True)
    total_bases = sum(len(o) for o in oligos)
    payload_size = int(meta["tag"].get("LEN", 0))
    density = payload_size * 8 / total_bases if total_bases else 0

    print(f"AeonScript block inspection — {fasta_path}")
    print(f"{'-' * 60}")
    print(f"  oligos       : {len(oligos)}")
    print(f"  total bases  : {total_bases}")
    print(f"  payload bytes: {payload_size}")
    print(f"  density      : {density:.3f} bits/base utiles")
    print(f"  errors fixed : {meta['errors_corrected']}")
    print(f"\n  Semantic tag:")
    for k, v in meta["tag"].items():
        val = v if len(v) <= 80 else v[:77] + "..."
        print(f"    {k:12s} = {val}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate this implementation against a vectors JSON file."""
    path = Path(args.vectors_json)
    if not path.exists():
        print(f"error: vectors file not found: {path}", file=sys.stderr)
        return 1
    data = json.loads(path.read_text(encoding="utf-8"))

    passed = 0
    failed: list[str] = []
    for vec in data.get("vectors", []):
        vid = vec["id"]
        expected_payload = bytes.fromhex(vec["input"]["payload_hex"])
        expected_oligos = vec["expected"]["oligos"]
        try:
            decoded = decode_oligos(expected_oligos)
            if decoded == expected_payload:
                passed += 1
            else:
                failed.append(f"{vid}: decoded bytes mismatch")
        except Exception as e:
            failed.append(f"{vid}: {type(e).__name__}: {e}")

    total = passed + len(failed)
    print(f"AeonScript conformance — {path}")
    print(f"{'-' * 60}")
    print(f"  spec version : {data.get('spec_version', '?')}")
    print(f"  l1 profile   : {data.get('l1_profile', '?')}")
    print(f"  l4 codec     : {data.get('l4_codec', '?')}")
    print(f"  vectors      : {total}")
    print(f"  passed       : {passed}")
    print(f"  failed       : {len(failed)}")
    for f in failed:
        print(f"    ✗ {f}")
    return 0 if not failed else 2


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aeonscript",
        description=(
            f"AeonScript reference codec v{__version__} (spec v{__spec_version__}). "
            "See https://aeonscript.org"
        ),
    )
    parser.add_argument("-V", "--version", action="version", version=f"aeonscript {__version__}")
    subs = parser.add_subparsers(dest="command", required=True)

    p_encode = subs.add_parser("encode", help="encode a file into DNA oligos (FASTA)")
    p_encode.add_argument("input", help="path to the file to encode")
    p_encode.add_argument("-o", "--output", help="output FASTA path (default: <input>.oligos.fasta)")
    p_encode.add_argument(
        "-t",
        "--mime-type",
        default="application/octet-stream",
        help="MIME type to declare in the L5 tag (default: application/octet-stream)",
    )
    p_encode.add_argument("--id", help="block ID (default: input filename)")
    p_encode.set_defaults(func=cmd_encode)

    p_decode = subs.add_parser("decode", help="decode DNA oligos back to the original payload")
    p_decode.add_argument("fasta", help="path to the FASTA file of oligos")
    p_decode.add_argument("-o", "--output", help="output payload path (default: <fasta>.decoded.bin)")
    p_decode.set_defaults(func=cmd_decode)

    p_inspect = subs.add_parser("inspect", help="show stats and tag of a FASTA block")
    p_inspect.add_argument("fasta", help="path to the FASTA file of oligos")
    p_inspect.set_defaults(func=cmd_inspect)

    p_validate = subs.add_parser(
        "validate",
        help="validate this implementation against a JSON vectors file",
    )
    p_validate.add_argument(
        "vectors_json",
        help="path to a vectors JSON (e.g. spec/test-vectors/vectors-l1-l5.json)",
    )
    p_validate.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
