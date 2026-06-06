"""PRBS scrambler — uniformizes byte distribution before L1 encoding.

Standard technique in DNA storage codecs to balance GC and break repetitive
patterns. Uses xorshift32 PRNG with a fixed seed; XOR is self-inverse so
the same function descrambles.

The seed is fixed (not transmitted) — both encoder and decoder MUST agree.
"""

from __future__ import annotations

SCRAMBLER_SEED = 0xDEADBEEF


def _xorshift32(state: int) -> int:
    state ^= (state << 13) & 0xFFFFFFFF
    state ^= state >> 17
    state ^= (state << 5) & 0xFFFFFFFF
    return state & 0xFFFFFFFF


def scramble(data: bytes, seed: int = SCRAMBLER_SEED) -> bytes:
    """XOR each byte with a pseudo-random byte stream."""
    state = seed & 0xFFFFFFFF
    out = bytearray(len(data))
    for i, b in enumerate(data):
        state = _xorshift32(state)
        out[i] = b ^ (state & 0xFF)
    return bytes(out)


# Symmetric: XOR is self-inverse
descramble = scramble
