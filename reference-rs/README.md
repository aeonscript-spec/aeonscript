# aeonscript (Rust reference)

Rust reference implementation of the [AeonScript](https://aeonscript.org) open standard for DNA-based information archival.

**Status** : v0.1 skeleton. L1, L5, and the scrambler are implemented and pass round-trip tests against the Python and Node references. L4 (Reed-Solomon) uses `reed-solomon-erasure` and ships as integration target.

This crate is the canonical Rust implementation and the target for the production pipeline (per the [ROADMAP](https://github.com/aeonscript-spec/aeonscript/blob/main/ROADMAP.md) Phase 2). For most users, the [Python reference](../reference/) is easier to drive and audit; the Rust port exists to demonstrate cross-language portability and to provide a 100× performance baseline.

## Use

```rust
use aeonscript::{encode_bytes, decode_oligos};

let payload = b"The first message I want to preserve.";
let oligos = encode_bytes(payload, "text/plain", "tutorial-1")?;
let recovered = decode_oligos(&oligos)?;
assert_eq!(recovered.as_slice(), payload);
```

## Command-line interface

The crate ships an `aeonscript` binary that encodes any file into a FASTA pool
of oligos and decodes it back, byte-for-byte:

```bash
cargo build --release

# Encode an arbitrary file into a DNA oligo pool (FASTA)
./target/release/aeonscript encode photo.jpg -o pool.fasta --mime image/jpeg --id photo

# Decode the pool back to the original bytes
./target/release/aeonscript decode pool.fasta -o photo.out.jpg
#  → photo.out.jpg is identical to photo.jpg

aeonscript --help      # full option list
aeonscript --version   # crate + spec version
```

`encode` options: `-o/--out`, `--mime`, `--id`, `--len` (target oligo length, default 200, min 64).
`decode` options: `-o/--out`. Without `-o`, output goes to stdout.

## Run

```bash
cargo build --release
cargo test
cargo run --example smoke_test
cargo run --bin aeonscript -- --help
```

## Status of layers

| Layer | Status |
|-------|--------|
| L1 — Physical | ✓ implemented (mirrors `aeonscript.physical`) |
| L2 — Multiplexing | not in v0.1 (draft spec in `spec/drafts/`) |
| L3 — Random access | not in v0.1 |
| L4 — Reed-Solomon | ✓ implemented via `reed-solomon-erasure` |
| L5 — Semantic tags | ✓ implemented |
| L6 — Presentation | not in v0.1 |
| L7 — Application | not in v0.1 |
| Bio-safety | scaffold present, hazards DB loaded from JSON |
| Scrambler | ✓ xorshift32, byte-identical to Python/Node refs |

## Conformance

This crate is validated against the canonical L1+L5 test vectors at [`spec/test-vectors/vectors-l1-l5.json`](../spec/test-vectors/vectors-l1-l5.json). See `tests/conformance.rs`.

## License

MIT — see [LICENSE](../LICENSE) at the repository root.
