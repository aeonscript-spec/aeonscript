# Wire Format by Example

This document walks through what AeonScript actually puts on the DNA, byte by byte.

If you've read the [spec](../spec/SPEC-v0.1.md) and want to *see* what a real block looks like, you're in the right place.

---

## A minimum block

Let's encode the 12-byte payload `b"Hello world."` as `text/plain` with block ID `tutorial-1`.

### Step 1 — L5 semantic tag

The encoder builds an ASCII tag string:

```
|AEONSCRIPT=0.1;L1=L1-4;L4=rs255-223;TYPE=text/plain;LEN=12;ID=tutorial-1;CHECKSUM=sha256:64ec88ca00b268e5ba1a35678a1b5316d212f4f366b2477232534a8aeca37f3c|
```

That's 168 ASCII bytes. It's not space-efficient — that's the cost of being human-readable and self-describing. Future revisions may add a binary alternative.

The tag is then prepended to the payload:

```
[ 168 bytes of tag ASCII ][ 12 bytes of "Hello world." ]
```

→ 180 bytes total at this stage.

### Step 2 — L4 Reed-Solomon

The encoder splits the 180-byte stream into 223-byte blocks (zero-padded if needed):

```
[ 180 bytes data ][ 43 bytes zeros ] = 223 bytes
```

It then computes a 32-byte parity using RS(255, 223):

```
[ 223 bytes data+pad ][ 32 bytes parity ] = 255 bytes
```

→ 255 bytes after L4.

### Step 3 — Scrambler (between L4 and L1)

The 255 bytes are XOR-ed with a deterministic xorshift32 stream (seed `0xDEADBEEF`).

This **does not change the length** — still 255 bytes — but makes the bit distribution uniform. Without this step, ASCII text (which has a heavy bit-0 bias in the high nibble) would produce DNA with skewed GC content and frequent A/T homopolymer runs.

### Step 4 — L1 physical encoding

Each scrambled byte (8 bits) maps to 4 DNA bases (2 bits per base) using the L1-4 mapping:

| Bits | Base (canonical permutation) |
|---|---|
| `00` | A |
| `01` | C |
| `10` | G |
| `11` | T |

So one byte `0xB2 = 0b10110010` encodes (LSB-first) as:
- `10` → G
- `00` → A
- `11` → T
- `10` → G

→ `GATG`.

The encoder also prepends a 4-base **permutation prefix** to each oligo, so the decoder knows which permutation was used:

| Prefix | Permutation index |
|---|---|
| `ACGT` | 0 (canonical) |
| `AGCT` | 1 |
| `TCGA` | 2 |
| `CATG` | 3 |
| `GTAC` | 4 |

The encoder tries permutation 0 first. If the resulting oligo violates a biochemical constraint (homopolymer > 8, GC out of [25%, 75%], forbidden motif), it tries the next permutation. With 5 permutations and a scrambled input, satisfaction probability per oligo is > 99.7%.

### Step 5 — Split into oligos

The 255 bytes (→ 1020 bases body) are split into oligos of target length 200 bases.

Each oligo: 4-base prefix + (196 bases body = 49 bytes).

→ 255 / 49 ≈ 5.2 oligos → 6 oligos (last one shorter).

---

## Concrete numbers for `"Hello world."`

After encoding with `mime_type="text/plain"`, `block_id="tutorial-1"`:

```
Payload:               12 bytes
+ L5 tag:             180 bytes total
+ L4 padding:         223 bytes (zero-padded to RS block size)
+ L4 RS parity:       255 bytes (with 32 parity bytes)
After scrambler:      255 bytes (length unchanged)
L1 encoded:           6 oligos × ~200 bases = ~1080 bases
```

**Density**: 12 bytes payload / 1080 bases = **0.089 bits utiles/base** for this tiny example.

Why so low? **Tag overhead dominates** when payloads are small. For payloads ≥ 10 KB, the tag becomes negligible and density approaches `2 × (223/255) ≈ 1.75 bits/base` for L1-4.

For payloads ≥ 1 MB, the practical density is what matters most — see [comparison-vs-alternatives.md](comparison-vs-alternatives.md).

---

## Reading the wire

A decoder receives the oligos in any order (DNA storage typically reads via PCR amplification then high-throughput sequencing — order is not preserved). For v0.1, AeonScript assumes the caller preserves order. **L3 v0.2 will add position metadata per oligo.**

Given the ordered oligos, the decoder:

1. For each oligo: read the 4-base prefix → identify permutation → decode the body bytes.
2. Concatenate all body bytes → 255-byte (or N × 255-byte) RS-encoded stream.
3. Apply the inverse scrambler (same xorshift32 stream, XOR is self-inverse).
4. For each 255-byte block: run RS decode → recover 223 bytes (corrects up to 16 errors).
5. Strip the trailing parity → concatenate to get the tag+payload+padding stream.
6. Parse the L5 tag: find `|` at offset 0, find closing `|`, parse `KEY=VALUE` pairs.
7. Read `LEN` from the tag → that many bytes after the closing `|` are the payload.
8. Discard the rest (which is RS block padding).

---

## A few invariants that any conformant implementation MUST preserve

1. **Tag is ASCII** — never UTF-8 byte sequences in the tag itself.
2. **Permutation prefix is exactly 4 bases** — never elided, never longer.
3. **Scrambler seed is fixed** (`0xDEADBEEF` in v0.1) — both encoder and decoder MUST agree.
4. **The `LEN` field is the original payload length in bytes**, *not* including tag, parity, or padding.
5. **The `CHECKSUM` field, if present, covers the original payload bytes only** — not the tag, not the L4 codeword.
6. **Oligos can be returned in any order, but the decoder receives them in encoding order in v0.1.** L3 v0.2 will lift this restriction.

---

## See it for yourself

The 10 canonical test vectors in [`spec/test-vectors/vectors-l1-l5.json`](../spec/test-vectors/vectors-l1-l5.json) show exact byte-by-byte inputs and oligo outputs for the L1+L5-only path (no Reed-Solomon, so easier to inspect manually).

For the full pipeline, run [the encode demo](../reference/examples/encode_demo.py).
