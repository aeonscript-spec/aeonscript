"""Layer 4 — Transport: Reed-Solomon error correction over GF(256).

Pure-Python implementation of systematic RS codes. No external dependencies.

Default parameters per SPEC-v0.1 §3.1:
    n=255, k=223, parity=32 → corrects up to 16 byte errors per codeword.

Reference algorithm follows the Wikiversity Reed-Solomon tutorial,
adapted for clarity. Primitive polynomial 0x11d (standard CCSDS choice).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# GF(256) arithmetic
# ---------------------------------------------------------------------------

_PRIM = 0x11D  # Primitive polynomial x^8 + x^4 + x^3 + x^2 + 1
_FIELD_SIZE = 256

# Pre-computed log/antilog tables
_GF_EXP: list[int] = [0] * 512
_GF_LOG: list[int] = [0] * 256


def _init_tables() -> None:
    x = 1
    for i in range(255):
        _GF_EXP[i] = x
        _GF_LOG[x] = i
        x <<= 1
        if x & 0x100:
            x ^= _PRIM
    for i in range(255, 512):
        _GF_EXP[i] = _GF_EXP[i - 255]


_init_tables()


def gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return _GF_EXP[_GF_LOG[a] + _GF_LOG[b]]


def gf_div(a: int, b: int) -> int:
    if b == 0:
        raise ZeroDivisionError("GF(256) division by zero")
    if a == 0:
        return 0
    return _GF_EXP[(_GF_LOG[a] + 255 - _GF_LOG[b]) % 255]


def gf_pow(x: int, power: int) -> int:
    return _GF_EXP[(_GF_LOG[x] * power) % 255]


def gf_inv(x: int) -> int:
    return _GF_EXP[255 - _GF_LOG[x]]


# ---------------------------------------------------------------------------
# Polynomial arithmetic over GF(256)
# ---------------------------------------------------------------------------


def poly_scale(p: list[int], x: int) -> list[int]:
    return [gf_mul(c, x) for c in p]


def poly_add(p: list[int], q: list[int]) -> list[int]:
    r = [0] * max(len(p), len(q))
    for i, c in enumerate(p):
        r[i + len(r) - len(p)] = c
    for i, c in enumerate(q):
        r[i + len(r) - len(q)] ^= c
    return r


def poly_mul(p: list[int], q: list[int]) -> list[int]:
    r = [0] * (len(p) + len(q) - 1)
    for j, qj in enumerate(q):
        for i, pi in enumerate(p):
            r[i + j] ^= gf_mul(pi, qj)
    return r


def poly_eval(p: list[int], x: int) -> int:
    """Horner-rule polynomial evaluation."""
    y = p[0]
    for c in p[1:]:
        y = gf_mul(y, x) ^ c
    return y


# ---------------------------------------------------------------------------
# Reed-Solomon encoding
# ---------------------------------------------------------------------------


def rs_generator_poly(nsym: int) -> list[int]:
    """Build the generator polynomial g(x) = ∏(x - α^i) for i=0..nsym-1."""
    g = [1]
    for i in range(nsym):
        g = poly_mul(g, [1, gf_pow(2, i)])
    return g


def rs_encode_msg(msg_in: bytes, nsym: int) -> bytes:
    """Encode bytes with `nsym` parity symbols, returning systematic codeword."""
    if len(msg_in) + nsym > 255:
        raise ValueError(
            f"Message too long: len(msg)+nsym={len(msg_in) + nsym} > 255"
        )
    gen = rs_generator_poly(nsym)
    msg_out = list(msg_in) + [0] * nsym

    for i in range(len(msg_in)):
        coef = msg_out[i]
        if coef != 0:
            for j in range(1, len(gen)):
                msg_out[i + j] ^= gf_mul(gen[j], coef)

    msg_out[: len(msg_in)] = list(msg_in)
    return bytes(msg_out)


# ---------------------------------------------------------------------------
# Reed-Solomon decoding
# ---------------------------------------------------------------------------


def rs_calc_syndromes(msg: bytes, nsym: int) -> list[int]:
    return [poly_eval(list(msg), gf_pow(2, i)) for i in range(nsym)]


def rs_find_error_locator(syndromes: list[int], nsym: int) -> list[int]:
    """Berlekamp-Massey algorithm."""
    err_loc = [1]
    old_loc = [1]

    for i in range(nsym):
        delta = syndromes[i]
        for j in range(1, len(err_loc)):
            delta ^= gf_mul(err_loc[-(j + 1)], syndromes[i - j])
        old_loc = old_loc + [0]
        if delta != 0:
            if len(old_loc) > len(err_loc):
                new_loc = poly_scale(old_loc, delta)
                old_loc = poly_scale(err_loc, gf_inv(delta))
                err_loc = new_loc
            err_loc = poly_add(err_loc, poly_scale(old_loc, delta))

    # Strip leading zeros
    while err_loc and err_loc[0] == 0:
        err_loc.pop(0)

    return err_loc


def rs_find_errors(err_loc: list[int], nmess: int) -> list[int]:
    """Chien search: find error positions."""
    errs = len(err_loc) - 1
    err_pos = []
    for i in range(nmess):
        if poly_eval(err_loc, gf_pow(2, i)) == 0:
            err_pos.append(nmess - 1 - i)
    if len(err_pos) != errs:
        raise ValueError(
            f"Too many errors to correct: found {len(err_pos)}, expected {errs}"
        )
    return err_pos


def rs_correct_errata(
    msg: list[int], syndromes: list[int], err_pos: list[int]
) -> list[int]:
    """Forney algorithm: compute and apply error values."""
    coef_pos = [len(msg) - 1 - p for p in err_pos]
    err_loc = [1]
    for i in coef_pos:
        x = gf_pow(2, i)
        err_loc = poly_mul(err_loc, [x, 1])

    err_eval = poly_mul(syndromes[::-1], err_loc)[len(err_loc) - 1 :]
    x_vals = [gf_pow(2, c) for c in coef_pos]
    e = [0] * len(msg)

    for i, xi in enumerate(x_vals):
        xi_inv = gf_inv(xi)
        err_loc_prime = 1
        for j, xj in enumerate(x_vals):
            if j != i:
                err_loc_prime = gf_mul(err_loc_prime, 1 ^ gf_mul(xi_inv, xj))
        y = poly_eval(err_eval[::-1], xi_inv)
        y = gf_mul(gf_pow(xi, 1), y)
        if err_loc_prime == 0:
            raise ValueError("Forney algorithm: zero locator derivative")
        magnitude = gf_div(y, err_loc_prime)
        e[err_pos[i]] = magnitude

    return [a ^ b for a, b in zip(msg, e)]


def rs_decode_msg(codeword: bytes, nsym: int) -> tuple[bytes, int]:
    """Decode a Reed-Solomon codeword.

    Returns (corrected_message_bytes, n_errors_corrected).
    Raises ValueError if uncorrectable.
    """
    msg = list(codeword)
    syndromes = rs_calc_syndromes(msg, nsym)
    if max(syndromes) == 0:
        return bytes(msg[:-nsym]), 0  # No errors

    err_loc = rs_find_error_locator(syndromes, nsym)
    err_pos = rs_find_errors(err_loc, len(msg))
    corrected = rs_correct_errata(msg, syndromes, err_pos)

    # Verify
    new_syn = rs_calc_syndromes(bytes(corrected), nsym)
    if max(new_syn) != 0:
        raise ValueError("Reed-Solomon decode failed (syndromes nonzero after correction)")

    return bytes(corrected[:-nsym]), len(err_pos)


# ---------------------------------------------------------------------------
# High-level convenience
# ---------------------------------------------------------------------------


def encode_with_ecc(data: bytes, nsym: int = 32, block_size: int = 223) -> bytes:
    """Split data into RS blocks of size `block_size` and encode each."""
    out = bytearray()
    for i in range(0, len(data), block_size):
        chunk = data[i : i + block_size]
        # Pad last block if needed
        if len(chunk) < block_size:
            pad = block_size - len(chunk)
            chunk = chunk + bytes([0] * pad)
            out.extend(rs_encode_msg(chunk, nsym))
            # Mark padding length in a trailer byte (simple convention)
            # For v0.1, padding is tracked at the L5 tag level via LEN field
        else:
            out.extend(rs_encode_msg(chunk, nsym))
    return bytes(out)


def decode_with_ecc(data: bytes, nsym: int = 32, block_size: int = 223) -> tuple[bytes, int]:
    """Decode RS-encoded data, returning (payload, total_errors_corrected)."""
    full_block = block_size + nsym
    if len(data) % full_block != 0:
        raise ValueError(
            f"Data length {len(data)} not a multiple of full block size {full_block}"
        )

    out = bytearray()
    total_errors = 0
    for i in range(0, len(data), full_block):
        codeword = data[i : i + full_block]
        msg, n_errs = rs_decode_msg(codeword, nsym)
        out.extend(msg)
        total_errors += n_errs
    return bytes(out), total_errors
