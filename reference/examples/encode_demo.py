"""AeonScript end-to-end demo.

Encodes a short passage of text into DNA oligos, displays the result,
injects random errors to simulate sequencing noise, and verifies that
Reed-Solomon recovers the original.

Run:
    python encode_demo.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

# Allow running from anywhere
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aeonscript import encode_bytes, decode_oligos


PASSAGE = (
    "« La mémoire de l'humanité ne devrait pas être propriétaire. »\n\n"
    "Ceci est un test du codec de référence AeonScript v0.1. "
    "Le texte que vous lisez vient d'être encodé en ADN, puis décodé. "
    "S'il s'affiche correctement, le round-trip a fonctionné — y compris "
    "après injection d'erreurs aléatoires simulant le séquençage Illumina."
).encode("utf-8")


def banner(title: str) -> None:
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def inject_errors(oligos: list[str], n_errors: int, seed: int = 42) -> list[str]:
    """Randomly mutate `n_errors` bases across the oligos."""
    rng = random.Random(seed)
    mutated = [list(o) for o in oligos]
    for _ in range(n_errors):
        # Choose a random (oligo_idx, base_idx)
        oligo_idx = rng.randint(0, len(mutated) - 1)
        base_idx = rng.randint(0, len(mutated[oligo_idx]) - 1)
        current = mutated[oligo_idx][base_idx]
        alternatives = [b for b in "ACGT" if b != current]
        mutated[oligo_idx][base_idx] = rng.choice(alternatives)
    return ["".join(o) for o in mutated]


def main() -> int:
    banner("AeonScript Demo — Encode")
    print(f"Original payload: {len(PASSAGE)} bytes")
    print(f"First 200 bytes preview:\n  {PASSAGE[:200].decode('utf-8')!r}")
    print()

    oligos = encode_bytes(
        PASSAGE,
        mime_type="text/plain",  # v0.1: MIME params (;...) reserved for v0.2 escaping
        block_id="demo-fr-1",
        extra_tag_fields={
            "AUTHORS": "AeonScript Contributors",
            "LICENSE": "CC-BY-SA-4.0",
            "TIER": "demo",
        },
    )

    total_bases = sum(len(o) for o in oligos)
    bits_in = len(PASSAGE) * 8
    print(f"Encoded into {len(oligos)} oligos, total {total_bases} bases.")
    print(f"Average oligo length: {total_bases / len(oligos):.0f} bases.")
    print(f"Theoretical density (Shannon, 2 bits/base): {bits_in / total_bases:.3f}")
    print("  (lower than 2 because of RS parity + L5 tag overhead — expected.)")
    print()

    banner("Sample oligos (first 3)")
    for i, o in enumerate(oligos[:3]):
        print(f"  [{i}] ({len(o)} bases) {o[:60]}{'...' if len(o) > 60 else ''}")

    banner("AeonScript Demo — Round-trip without errors")
    decoded, meta = decode_oligos(oligos, return_metadata=True)
    if decoded == PASSAGE:
        print("  ✓ Round-trip OK — bytes identical.")
    else:
        print("  ✗ MISMATCH!")
        return 1
    print("  Semantic tag parsed:")
    for k, v in meta["tag"].items():
        print(f"    {k:12s} = {v}")
    print(f"  Errors corrected: {meta['errors_corrected']}")

    banner("AeonScript Demo — Round-trip with injected errors")
    n_err = 4  # within RS(255,223) capacity per block (16 errors/block)
    print(f"  Injecting {n_err} random base substitutions...")
    noisy = inject_errors(oligos, n_err)

    try:
        decoded2, meta2 = decode_oligos(noisy, return_metadata=True)
        if decoded2 == PASSAGE:
            print("  ✓ Reed-Solomon recovered the original payload.")
            print(f"  Errors corrected at decode: {meta2['errors_corrected']}")
        else:
            print("  ✗ Decoded payload differs from original (despite no exception).")
            return 1
    except Exception as e:
        print(f"  ✗ Decode failed: {type(e).__name__}: {e}")
        return 1

    banner("AeonScript Demo — Done")
    print("  Implementation status: L1 + L4 + L5 functional.")
    print("  Next: L2 (multiplexing), L3 (PCR random access), AI-native L4.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
