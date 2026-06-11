# Comparison vs other DNA storage codecs

AeonScript is not the first DNA storage codec — and it is not pretending to be. This document situates AeonScript honestly against the established alternatives.

---

## TL;DR

| Codec | Year | Bits/base achieved | Self-describing | Layered | Open spec | Reference impl |
|---|---|---|---|---|---|---|
| Goldman et al. | 2013 | 0.33 | ❌ | ❌ | partial (paper) | none |
| DNA Fountain (Erlich & Zielinski) | 2017 | 1.57 | ❌ | ❌ | yes (paper + code) | Python (GitHub) |
| HEDGES (Press et al.) | 2020 | ~1.6 | ❌ | ❌ | yes (paper + code) | C++ |
| Microsoft cluster code | 2020 | ~1.5 | ❌ | partial | partial | proprietary |
| Catalog combinatorial | 2019+ | varies | ❌ | ❌ | trade secret | proprietary |
| **AeonScript v0.1** | **2026** | **~1.4** | **✓** | **✓** | **✓** | **Python + Node** |
| AeonScript v0.2 (planned) | 2027 | ~2.2 | ✓ | ✓ | ✓ | Python + Rust + WASM |

**AeonScript's distinguishing claim is not raw density.** It is *interoperability and survivability*. We trade ~10–15% density vs. DNA Fountain for self-description, versioning, and layered evolution.

---

## What AeonScript is NOT trying to be

- **Not the densest codec.** DNA Fountain achieves ~85% of the Shannon limit. AeonScript v0.1 is at ~70% because tags eat ~5–15% per small block. v0.2 will close most of this gap.
- **Not a hot-storage solution.** No DNA codec is. Cold archive (>10 year retention) is the target.
- **Not a synthesis or sequencing pipeline.** AeonScript defines the *format*. The biology stays with Twist, IDT, Illumina, Nanopore.
- **Not a Microsoft replacement.** Microsoft's cluster codec is excellent at what it does (single-vendor, single-codec, single-decoder). AeonScript exists because *every vendor having its own incompatible codec* is the problem.

---

## Per-codec breakdown

### Goldman et al. (2013) — *"Towards practical, high-capacity, low-maintenance information storage in synthesized DNA"*

The pioneering paper. Encoded 739 KB of files (audio, text, image) at the EBI.

- **Density** : 0.33 bits/base (very conservative — used a ternary code to avoid homopolymers structurally).
- **Strengths** : structurally robust to L1 errors, no homopolymers possible by construction.
- **Weaknesses** : extremely low density (~6× worse than the Shannon limit), no self-description, no random access.
- **vs AeonScript** : AeonScript v0.1 is ~4× denser, but Goldman's ternary mapping is on our v0.2 roadmap as L1 profile `L1-3-goldman`.

### DNA Fountain (Erlich & Zielinski, 2017) — *"DNA Fountain enables a robust and efficient storage architecture"*

The benchmark. Encoded 2.1 MB at 1.57 bits/base using *fountain codes* (a class of erasure codes).

- **Density** : 1.57 bits/base, ~85% of the Shannon limit for the L1-4 channel.
- **Strengths** : near-optimal, well-tested, public code, used in subsequent industrial pipelines.
- **Weaknesses** : not self-describing (you must know the codec parameters externally), no semantic metadata, no random access (must decode the whole archive).
- **vs AeonScript** : DNA Fountain wins on raw density today. AeonScript wins on interoperability and survivability. *They are not competitive — they answer different questions.*

### HEDGES (Press et al., 2020) — *"HEDGES error-correcting code for DNA storage corrects indels and allows sequence constraints"*

The most robust codec to real DNA error patterns (insertions and deletions, not just substitutions).

- **Density** : ~1.6 bits/base.
- **Strengths** : handles insertion/deletion errors that confuse classical RS. Critical for Nanopore reads.
- **Weaknesses** : complex (custom Markov coding + arithmetic coding), no self-description, C++ only.
- **vs AeonScript** : HEDGES is the right inner-codec for high-error channels. AeonScript v0.2 may adopt HEDGES as L4 profile `L4-hedges`. Its layered architecture makes this swap clean — exactly the point of being layered.

### Microsoft cluster code (Organick et al., 2018+)

Microsoft Research's production codec for the automated read/write loop demo. Uses k-mer clustering + Reed-Solomon.

- **Density** : ~1.5 bits/base.
- **Strengths** : works in production end-to-end (synthesis → storage → sequencing → decode without human intervention).
- **Weaknesses** : proprietary, no open spec, no third-party implementation exists.
- **vs AeonScript** : Microsoft owns vertical integration. AeonScript exists because the **format** should not be vertically integrated. We hope Microsoft adopts AeonScript as their L4 profile while keeping their vertical pipeline.

### Catalog (combinatorial encoding)

Catalog Technologies' approach is fundamentally different — instead of synthesizing arbitrary sequences, they assemble combinations from a small library of pre-synthesized oligos. This radically lowers synthesis cost.

- **Density** : varies (a function of library size vs. payload).
- **Strengths** : economic at scale, fast write throughput.
- **Weaknesses** : proprietary, requires Catalog hardware, the encoded format is not portable.
- **vs AeonScript** : Catalog's *write process* is orthogonal to AeonScript. Catalog could (and we hope will) emit AeonScript-encoded oligos as its output format, with their combinatorial machinery underneath.

---

## What AeonScript adds that nothing else does

1. **Self-description.** A blob of DNA carrying an AeonScript block tells you, in its first ~75 bases, *which* codec was used. Every other codec listed here requires out-of-band knowledge.

2. **Versioning.** A v0.5 decoder will refuse v9.0 cleanly and tell you why — because the version is in the data.

3. **Layered evolution.** New chemistry (5mC, unnatural bases) updates L1 without breaking L5+. New error-correction (LDPC) updates L4 without breaking L1. No format break.

4. **Bio-safety as a normative requirement.** SPEC §9 mandates IGSC screening. No other codec specifies this at the format level.

5. **Random access protocol.** L3 (planned for v0.2) standardizes PCR-primer-based block retrieval. Today, every vendor invents this from scratch.

6. **An institutional governance plan.** Not just a paper or a GitHub repo — a roadmap to ISO/IEC submission, a planned non-profit foundation, and explicit invitation to libraries and archives.

---

## What we owe to the prior art

A lot. We are not original on most things:

- **Reed-Solomon over GF(256)** : Reed & Solomon 1960. We use the standard. No claim.
- **Channel coding for DNA** : Goldman 2013, Erlich 2017, Press 2020 figured out *most* of what works.
- **Layered protocols** : OSI 1984, TCP/IP. Borrowed wholesale.
- **Self-describing formats** : ASN.1, MIME, CBOR, JSON-LD all do this. We adapted.

What we're hoping to contribute is the **synthesis** — putting these pieces together in a way that maps onto DNA storage and survives a 200-year horizon.

---

## How AeonScript could lose

Brutal honesty:

- **If Microsoft / Twist / Catalog standardize together via the DNA Storage Alliance**, they could publish a competing open format. We'd hope for convergence; we'd accept being a feeder design.
- **If a foundation model (Evo 2 or descendants) makes the L4 layer trivially solvable**, AeonScript's careful Reed-Solomon may look quaint. The v0.2 AI-native L4 profile is our hedge.
- **If quantum-resistant encryption forces a wire-format break**, AeonScript v2.0 may diverge from v0.x. The layered architecture limits the blast radius, but it's a real risk.

---

## Where to go next

- The [SPEC](../spec/SPEC-v0.1.md) defines what AeonScript IS, normatively.
- The [ROADMAP](../ROADMAP.md) defines where it's going.
- The [MANIFESTO](../MANIFESTO.md) defines why.
- This document defines what it ISN'T.

---

*If you spot a misrepresentation of any of the above codecs, please [open an issue](https://github.com/aeonscript-spec/aeonscript/issues) — we want this comparison to be fair, not flattering.*
