# Frequently Asked Questions

If your question isn't answered here, please [open a Discussion](https://github.com/aeonscript-spec/aeonscript/discussions).

---

## General

### What is AeonScript in one sentence?

A layered, self-describing open standard for archiving arbitrary information on synthetic DNA, designed to remain readable for centuries.

### What problem does it solve?

Every DNA storage vendor (Microsoft, Twist, Catalog) currently uses its own proprietary encoding. A file written by one cannot be read by another, and none of them are documented in a way that would let a decoder in 2230 parse a file written in 2030. AeonScript provides the missing common format.

### Why "AeonScript"?

*Aeon* = a long unit of time (used informally for "an age" or "a very long period"). *Script* = writing system / code. Together: the writing of long time.

### Why was this not called "BioCodex"?

Biocodex S.A. is a real French pharmaceutical company that owns the trademark. We changed the name before the first public commit specifically to avoid a trademark dispute. Lesson: search trademarks before naming.

### Is this affiliated with Microsoft, Twist, Arc Institute, etc.?

No. AeonScript is an independent, open-source project. None of those organisations have endorsed or been formally contacted at the time of v0.1 publication. The [MANIFESTO](MANIFESTO.md) lists them as *outreach targets* — institutions we would like to engage in Phase 1.

---

## Technical

### Why a 7-layer architecture?

The 7-layer model is borrowed from OSI networking. It's not load-bearing as a number — the point is **layers are independently versionable**. A change to the alphabet (L1) doesn't break the application format (L7). A new error-correction scheme (L4) doesn't break the file index (L3).

### Why not just use DNA Fountain?

DNA Fountain (Erlich 2017) is excellent at what it does — high-density encoding. But it's not self-describing, not layered, and not versioned. AeonScript can use DNA Fountain as one of its L4 codec profiles. They're not competitive — they answer different questions. See [comparison-vs-alternatives.md](docs/comparison-vs-alternatives.md).

### Why is the L1 codec so simple in v0.1?

The current 2-bit-per-base mapping with a PRBS scrambler is *intentionally permissive* (allows runs up to 8, GC% in [25%, 75%]). It's a placeholder until v0.2 ships a Goldman-style ternary or RLL-constrained codec. The reason for shipping v0.1 with a simple codec is to validate the overall architecture before optimising the leaves.

### Why use the `reedsolo` library instead of implementing Reed-Solomon from scratch?

We tried. The from-scratch implementation had a bug in the Forney algorithm that wasn't caught locally (no Python install during development). `reedsolo` is a single, BSD-3, ~200-line library used in QR-code decoders and CCSDS deep-space links. **Correctness via a proven library beats aesthetic purity via an unverified one.**

### How much data can I actually fit?

For payloads ≥ 10 KB: roughly **1.4 bits/base utiles** in v0.1 (75% efficiency vs Shannon limit, due to RS parity + L5 tag overhead). v0.2 targets ~2.2 bits/base. Practical density: ~80–90 GB per dollar of synthesis at 2026 prices, projected to ~5 TB/$ by 2030.

### Does the spec depend on a specific AI model?

No. The spec defines an *interface* for AI-driven L4 codec selection. The model (Evo 2, Caduceus, HyenaDNA, future ones) is a runtime dependency, not a normative requirement. Today, the entire codec works with zero AI involvement.

### Why ASCII tags? They waste a lot of bases.

We accept the ~5–15% overhead for two reasons: (1) tags are human-readable when debugging a corrupted file, (2) any binary alternative would require a separate parser ecosystem. v0.2 may add an optional CBOR-binary tag profile alongside the ASCII default.

### What's the smallest payload that makes sense?

Mathematically, any size > 0. Practically, payloads under ~1 KB have so much tag overhead they're not economical — use a regular file. AeonScript is for archival of meaningful content (≥ 10 KB, typically ≥ 1 MB).

### How does it handle insertion/deletion errors?

v0.1 handles only substitution errors via Reed-Solomon. Real DNA (especially Nanopore reads) has indels. v0.2 will add an `L4-hedges` profile based on Press et al. 2020 HEDGES codes.

### Why is bio-safety a normative requirement?

Because DNA storage relies on a DNA synthesis pipeline, and synthesis can in principle produce biologically active sequences. If we are going to standardize a format whose adoption increases the volume of DNA being synthesized, we have an ethical obligation to bake in the same screening protocol the synthesis industry already uses voluntarily (IGSC). See [SPEC §9](spec/SPEC-v0.1.md#9-bio-safety-protocol-cross-cutting-mandatory).

---

## Adoption / governance

### Who controls AeonScript?

Currently: the maintainers (initially the original author). Long-term: a non-profit foundation modelled on Mozilla / Linux Foundation, governed by institutional members (libraries, archives, universities). See [ROADMAP](ROADMAP.md) Phase 4.

### Can I use AeonScript commercially?

Yes. Code is MIT, spec is CC-BY-SA. No royalties. No CLA. The trademark on "AeonScript" itself is a separate matter — see below.

### Can I call my product "AeonScript-Compliant"?

Only if it passes the [conformance suite](spec/CONFORMANCE.md). A formal certification process will exist in Phase 5 of the roadmap. Until then, declaring conformance is on the honour system — but the canonical test vectors make verification mechanical.

### Will AeonScript be standardized by ISO?

That is the goal (Phase 5 of the roadmap, 2028–2030). ISO/IEC JTC 1 is the likely venue.

### How is this funded?

Currently: pure volunteer effort. The plan is to seek philanthropic funding (institutional grants, possibly an ERC Advanced or Synergy grant) once there's traction. Approximately €5M would cover Phase 0 through Phase 4 over 5 years.

### How can I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md). Highest-priority needs at v0.1:

- Validate the spec against your DNA storage use case
- Implement the codec in a language other than Python/Node (Rust, Go, C++)
- Add L2/L3 designs (the hardest open work)
- Help with academic peer review
- Translate the manifesto and key docs

### What if I disagree with a spec decision?

Open a [Discussion](https://github.com/aeonscript-spec/aeonscript/discussions) of type "Spec discussion". The spec is a living document; major decisions are subject to public RFC for at least 2 weeks before adoption.

### What if Microsoft / Twist / Catalog forks this?

The MIT license permits forking. Our defence is institutional adoption: libraries and archives prefer the *open* standard. The trademark on "AeonScript" prevents a fork from being marketed under the same name.

---

## Practical

### Can I run AeonScript without Python?

Yes — the Node.js smoke test demonstrates the L1+L5 round-trip in any environment with Node 18+. A WASM build is on the v0.2 roadmap.

### What dependencies does the reference codec have?

One Python dependency: `reedsolo` (Reed-Solomon, BSD-3, ~200 lines). That's it. The L1, L5, and scrambler layers are pure stdlib.

### How fast is the reference codec?

Slow. It's the *reference*, not the *production* impl. Expect ~10 KB/s for encode and ~5 KB/s for decode on a modern laptop. A Rust port (v0.2 roadmap) will improve this by 100×.

### Where is the WASM build?

v0.2. For now, the Node smoke test runs in any JS environment with `Buffer` (Node, Deno, Bun).

### Can I encode files larger than 1 GB?

Technically yes, but it will take hours with the reference codec. Wait for the Rust port or use the [partial codec](reference/aeonscript/) as a library for your own optimized application.

### How do I report a bug?

[GitHub Issues](https://github.com/aeonscript-spec/aeonscript/issues), with a minimal reproduction. For security issues, see [SECURITY.md](.github/SECURITY.md).

### Will there be a Python `pip install aeonscript`?

When the codec passes its full test suite and the package metadata is finalised — likely v0.1.1.

---

*Still have questions? [Open a Discussion](https://github.com/aeonscript-spec/aeonscript/discussions). We'll add good ones to this FAQ.*
