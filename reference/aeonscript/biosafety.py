"""SPEC-v0.1 §9 — Bio-safety screening (stub).

A conformant AeonScript encoder MUST screen output oligos against a hazard
database before they are emitted for synthesis. This module provides a v0.1
stub implementation:

  * It loads a static hazard list shipped in `biosafety_hazards.json`.
  * Each entry is a short signature (≥ 20 bp) drawn from publicly-flagged
    sequences in the IGSC Harmonized Screening Protocol scope (toxins,
    select agents, etc.).
  * Screening = naive substring match against the candidate genome.

This is INTENTIONALLY a minimal stub. Real-world conformance requires:

  * The full IGSC database (not public; vendors maintain it internally).
  * BLAST-grade similarity search (90 % identity over ≥ 20 bp).
  * Reverse-complement and frameshift coverage.
  * Regular updates as the hazard list evolves.

The stub exists to make the API contract clear so v0.2 can swap in a
production engine without changing call sites.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class HazardMatch:
    """One match against a hazard signature."""

    oligo_index: int
    position: int
    signature_id: str
    signature_description: str
    matched_bases: str


class BioSafetyViolation(Exception):
    """Raised when an encoder is asked to emit oligos that match hazard sigs."""

    def __init__(self, matches: list[HazardMatch]):
        self.matches = matches
        msg = f"Bio-safety screening failed: {len(matches)} hazard match(es)\n"
        for m in matches[:5]:
            msg += (
                f"  - oligo #{m.oligo_index} pos {m.position}: "
                f"{m.signature_id} ({m.signature_description}) — "
                f"matched '{m.matched_bases}'\n"
            )
        if len(matches) > 5:
            msg += f"  ... and {len(matches) - 5} more.\n"
        super().__init__(msg)


def _load_hazard_db() -> list[dict]:
    """Load the hazard signature list shipped with the package."""
    try:
        data = (files("aeonscript") / "biosafety_hazards.json").read_text()
    except (FileNotFoundError, ModuleNotFoundError):
        # Fallback: relative path during development
        here = Path(__file__).parent
        data = (here / "biosafety_hazards.json").read_text()
    return json.loads(data)["signatures"]


def _reverse_complement(seq: str) -> str:
    comp = {"A": "T", "T": "A", "C": "G", "G": "C"}
    return "".join(comp[b] for b in reversed(seq))


def screen_oligos(oligos: Iterable[str]) -> list[HazardMatch]:
    """Screen a list of oligos against the hazard database.

    Returns a list of HazardMatch records. An empty list means safe.

    Per SPEC-v0.1 §9, this v0.1 implementation uses naive substring match
    (forward + reverse complement). A production implementation should use
    BLAST or equivalent for fuzzy matching at 90% identity over ≥ 20 bp.
    """
    sigs = _load_hazard_db()
    matches: list[HazardMatch] = []
    oligos = list(oligos)
    for i, oligo in enumerate(oligos):
        for sig in sigs:
            seq = sig["sequence"].upper()
            # Forward
            pos = oligo.find(seq)
            if pos >= 0:
                matches.append(HazardMatch(
                    oligo_index=i, position=pos,
                    signature_id=sig["id"],
                    signature_description=sig["description"],
                    matched_bases=seq,
                ))
            # Reverse complement
            rc = _reverse_complement(seq)
            pos = oligo.find(rc)
            if pos >= 0:
                matches.append(HazardMatch(
                    oligo_index=i, position=pos,
                    signature_id=sig["id"] + " (rev-comp)",
                    signature_description=sig["description"],
                    matched_bases=rc,
                ))
    return matches


def enforce_biosafety(oligos: Iterable[str]) -> None:
    """Raise BioSafetyViolation if any oligo matches a hazard signature.

    This is the function a conformant encoder MUST call before emitting
    oligos for synthesis (SPEC-v0.1 §9).
    """
    matches = screen_oligos(oligos)
    if matches:
        raise BioSafetyViolation(matches)
