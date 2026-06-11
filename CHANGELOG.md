# Changelog

All notable changes to AeonScript are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] — 2026-06-07

Initial public release.

### Added — spec

- Layered architecture (L1 through L7) modeled on OSI, with L1, L4, L5 fully normative in v0.1
- L1 physical layer: 4-letter alphabet (L1-4 profile), biochemical constraints (homopolymer ≤ 8, GC ∈ [25%, 75%], forbidden motifs), 4-base permutation prefix per oligo
- L4 transport layer: Reed-Solomon RS(255, 223) over GF(256) as default codec
- L5 session layer: self-describing semantic tags with mandatory keys (`AEONSCRIPT`, `L1`, `L4`, `TYPE`, `LEN`, `ID`) and reserved keys (`AUTHORS`, `LICENSE`, `CHECKSUM`, ...)
- §9 bio-safety protocol: mandatory IGSC screening before synthesis for conformant encoders
- 10 canonical L1+L5 test vectors in [`spec/test-vectors/vectors-l1-l5.json`](spec/test-vectors/vectors-l1-l5.json)
- [`spec/CONFORMANCE.md`](spec/CONFORMANCE.md) defining conformance levels and validation procedures

### Added — reference implementation

- Python package `aeonscript` (Python 3.10+), supporting encode/decode of arbitrary bytes
- Node.js smoke test demonstrating L1+L5 round-trip with no external dependencies
- xorshift32 PRBS scrambler to uniformise GC content
- pytest test suite covering L1, L4, L5, and end-to-end round-trip
- Encode demo script with simulated sequencing-error injection

### Added — repo & community

- MANIFESTO (vision, principles, governance plan)
- README, ROADMAP, CONTRIBUTING
- Dual license: MIT (code) + CC-BY-SA 4.0 (docs)
- GitHub issue templates (bug, feature, spec discussion), PR template
- CODE_OF_CONDUCT (Contributor Covenant)
- SECURITY policy with private vulnerability reporting + bio-safety channel
- CI workflow with Python 3.10/3.11/3.12 matrix, Node smoke test, ruff lint, spec/code version consistency check
- FAQ, GLOSSARY, quickstart tutorial, wire-format-by-example, comparison-vs-alternatives
- Landing page at <https://aeonscript.org> with custom domain + SSL

### Engineering notes

- Reed-Solomon implementation switched from a from-scratch GF(256) port (which had a Forney-algorithm bug uncovered locally because Python wasn't installed during development) to the proven `reedsolo` library (BSD-3, ~200 lines, used in QR-code decoders). Correctness via dependency beats aesthetic purity via unverified code.
- L1 constraints relaxed to homopolymer ≤ 8 and GC ∈ [25%, 75%] vs. the v0.2 target of ≤ 3 and [40%, 60%]. This is documented as a known limitation; a Goldman-ternary or RLL-constrained L1 profile is planned for v0.2.
- MIME types containing `;` (e.g. `text/plain; charset=utf-8`) now raise a `ValueError` rather than being silently truncated. Escape sequences in tag values are reserved for v0.2.

### Known limitations

- L2, L3, L6, L7 are described at the interface level only and not yet normative.
- No insertion/deletion error correction (substitutions only via Reed-Solomon).
- Bio-safety screening (§9) is documented but not implemented (stub planned for v0.1.1).
- Tag overhead is significant for small payloads (~75–150 bytes per block).
- No random access — blocks must be decoded in encoded order.

---

[0.1.0]: https://github.com/aeonscript-spec/aeonscript/releases/tag/v0.1.0
