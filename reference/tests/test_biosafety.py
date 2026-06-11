"""Tests for the bio-safety screening stub (SPEC §9)."""

from __future__ import annotations

import pytest

from aeonscript import (
    BioSafetyViolation,
    enforce_biosafety,
    screen_oligos,
)


def test_safe_oligos_pass():
    safe = [
        "ACGT" + "TTGCAGCGATGCTGCTCCAATATTAAGTTTTTGTAGAACGA",
        "AGCT" + "GGGTACGAAAAGGTGATCCGCTAGAAGCTGATACGAATTTAAGAA",
    ]
    matches = screen_oligos(safe)
    assert matches == [], f"Safe oligos triggered matches: {matches}"
    enforce_biosafety(safe)  # should not raise


def test_hazard_signature_caught_forward():
    """A test signature must be detected when present in forward orientation."""
    oligos = ["ACGT" + "AAAACGTACGTACGTACGTACGTGGGG"]
    matches = screen_oligos(oligos)
    assert len(matches) >= 1
    assert matches[0].signature_id == "TEST-SIG-001"
    with pytest.raises(BioSafetyViolation):
        enforce_biosafety(oligos)


def test_hazard_signature_caught_reverse_complement():
    """The reverse-complement of a hazard signature must also trigger."""
    # TEST-SIG-001 is "ACGTACGTACGTACGTACGT"
    # Its reverse complement is "ACGTACGTACGTACGTACGT" (it's a palindrome!)
    # Use a non-palindromic test instead: TEST-SIG-002 = CCCAAATTTGGGAAACCCAAA
    # Rev-comp = TTTGGGTTTCCCAAATTTGGG
    oligos = ["ACGT" + "AAATTTGGGTTTCCCAAATTTGGGCCC"]
    matches = screen_oligos(oligos)
    found_rev = [m for m in matches if "rev-comp" in m.signature_id]
    assert len(found_rev) >= 1


def test_enforce_raises_on_any_match():
    bad = ["ACGT" + "CCCAAATTTGGGAAACCCAAA" + "ACGT"]
    with pytest.raises(BioSafetyViolation) as exc:
        enforce_biosafety(bad)
    assert len(exc.value.matches) >= 1
