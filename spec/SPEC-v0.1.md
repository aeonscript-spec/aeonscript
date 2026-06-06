# AeonScript — Specification v0.1

**Status** : Draft
**Date** : May 2026
**License** : CC-BY-SA 4.0

---

## 0. Conventions

- **MUST**, **MUST NOT**, **SHALL**, **SHOULD**, **MAY** follow [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).
- All sequence examples are written 5' → 3' unless otherwise noted.
- All bit-level encodings are little-endian unless otherwise noted.
- Byte-strings are denoted `0xAB` (hex), bit-strings `0b1010`, ASCII strings in `"quotes"`.

---

## 1. Architectural overview

AeonScript is structured as **seven independent layers**, modeled on the OSI reference model:

```
┌─────────────────────────────────────────────┐
│ L7 — Application       (file-type formats)   │
├─────────────────────────────────────────────┤
│ L6 — Presentation      (compression, crypto) │
├─────────────────────────────────────────────┤
│ L5 — Session           (semantic tags)       │
├─────────────────────────────────────────────┤
│ L4 — Transport         (error correction)    │
├─────────────────────────────────────────────┤
│ L3 — Network           (PCR random access)   │
├─────────────────────────────────────────────┤
│ L2 — Data Link         (strand/frame mux)    │
├─────────────────────────────────────────────┤
│ L1 — Physical          (alphabet, encoding)  │
└─────────────────────────────────────────────┘
```

Each layer **MUST** be independently versionable. A change to L1 (e.g. adding 5-methylcytosine as a 5th symbol) **MUST NOT** break L5+.

This specification v0.1 fully defines **L1, L4, L5**. L2, L3, L6, L7 are described at the interface level only and reserved for v0.2+.

---

## 2. Layer 1 — Physical

### 2.1 Alphabet

A conformant L1 implementation **MUST** support the canonical 4-letter alphabet:

```
Σ₄ = { A, C, G, T }
```

It **MAY** declare support for the extended alphabets:

| Profile | Alphabet | Bits/symbol | Status |
|---------|----------|-------------|--------|
| `L1-4` | {A, C, G, T} | 2.00 | Canonical, MUST support |
| `L1-5m` | {A, C, G, T, 5mC} | 2.32 | Optional, MAY support |
| `L1-6` | {A, C, G, T, 5mC, 5hmC} | 2.58 | Experimental |

The active profile **MUST** be declared in the L5 session tag (see §4).

### 2.2 Base-to-bit mapping (canonical, profile `L1-4`)

| Base | 2-bit code |
|------|------------|
| A    | `00`       |
| C    | `01`       |
| G    | `10`       |
| T    | `11`       |

Bytes are encoded LSB-first into bases. Example:

```
Byte 0x4A = 0b01001010
            └┘└┘└┘└┘
             10  10 01 01     (LSB→MSB pairs)
             G   G  C  C
→ "GGCC"
```

A conformant decoder **MUST** parse bases right-to-left within a byte: the first base encodes the **least** significant bit pair.

### 2.3 Biochemical constraints

To remain synthesizable and sequenceable, an L1-encoded oligo **MUST** satisfy:

1. **Homopolymer limit** : no run of identical bases > 3.
   Example: `AAAA` is forbidden. `AAA` is allowed.
2. **GC content** : between 40 % and 60 % over any 50-base window.
3. **No forbidden motifs** : the conformant set **MUST** include at minimum:
   - `GGGGG` (G-quadruplex risk)
   - `ATATATATAT` (secondary structure risk)
   - Any motif declared in L5 tag `forbidden_motifs`

If raw 2-bit encoding violates a constraint, the encoder **MUST** apply a **mapping permutation** (different base assignment per byte) until the constraint is satisfied. The permutation index is encoded as a 2-bit prefix per oligo (24 possible permutations of 4 bases — 4 bits suffice; v0.1 reserves 4 bits and uses the lowest 5 permutations).

### 2.4 Oligo length

A standard AeonScript oligo:

- **MUST** be between 100 and 300 bases (current synthesis sweet spot)
- **SHOULD** be 200 bases by default
- The length is declared per-block in the L5 tag

---

## 3. Layer 4 — Transport / Error correction

### 3.1 Reed-Solomon over GF(256)

L4 v0.1 mandates **Reed-Solomon codes over GF(256)** for inner-oligo error correction.

Default parameters:

| Parameter | Value | Meaning |
|-----------|-------|---------|
| Symbol size | 8 bits | 1 byte |
| Codeword size (n) | 255 | Max RS block |
| Data size (k) | 223 | Effective payload |
| Parity (n-k) | 32 | Can correct up to 16 errors |

This is the **same** Reed-Solomon configuration used in CD audio, QR codes, and deep-space communications — chosen for proven reliability and tooling availability.

Encoders **MAY** declare alternative parameters via the L5 tag field `rs_params`.

### 3.2 LDPC outer code (block-level)

For protection against entire oligo losses (e.g. failed PCR amplification of one oligo), L4 v0.1 **SHOULD** add a **systematic LDPC outer code** over groups of N oligos.

Default : 1 parity oligo per 16 data oligos (recovers 1 lost oligo per block).

Reserved for v0.2 — v0.1 reference implementation uses simple **repetition** (each oligo encoded twice with different keys) as a placeholder.

### 3.3 Methylation hash channel (when L1 profile = `L1-5m`)

When the L1 profile uses 5mC, the methylation pattern of cytosines in the oligo **MUST** encode a 64-bit BLAKE3 hash of the unmethylated oligo bytes.

This provides **cross-layer error detection** : a silent point mutation will change the unmethylated sequence but not the hash → mismatch detected on decode.

---

## 4. Layer 5 — Session / Semantic tags

This is AeonScript's most distinctive feature. Every L5 block begins with a **semantic tag** that describes its own codec.

### 4.1 Tag wire format

A semantic tag is an ASCII-encoded structured prefix delimited by pipe characters `|`:

```
|<KEY>=<VALUE>;<KEY>=<VALUE>;...|
```

The tag is itself L1-encoded as standard bases (the `|` and `=` and `;` characters use specific reserved encodings — see §4.5).

### 4.2 Mandatory keys

Every AeonScript L5 tag **MUST** include:

| Key | Type | Example | Meaning |
|-----|------|---------|---------|
| `AEONSCRIPT` | version | `0.1` | Spec version this block conforms to |
| `L1` | profile | `L1-4` | Physical-layer alphabet profile |
| `L4` | codec | `rs255-223` | Error correction scheme |
| `TYPE` | MIME | `text/plain` | Payload content type |
| `LEN` | bytes | `4096` | Decoded payload length |
| `ID` | string | `42157` | Unique block identifier |

### 4.3 Optional keys

| Key | Example | Meaning |
|-----|---------|---------|
| `ENCRYPT` | `aes256-gcm` | Encryption scheme (L6) |
| `COMPRESS` | `zstd` | Compression scheme (L6) |
| `TIER` | `cold` | Storage tier hint |
| `CHECKSUM` | `blake3:abc123…` | Payload checksum |
| `AUTHORS` | `BnF` | Provenance metadata |
| `LICENSE` | `CC-BY-4.0` | Content license |
| `forbidden_motifs` | `GGGG,ATAT` | Extra L1 constraints |
| `rs_params` | `n=255,k=200` | Override RS defaults |

### 4.4 Tag examples

Minimal :
```
|AEONSCRIPT=0.1;L1=L1-4;L4=rs255-223;TYPE=text/plain;LEN=4096;ID=42157|
```

Cultural-archive use-case :
```
|AEONSCRIPT=0.1;L1=L1-5m;L4=rs255-223;TYPE=image/jp2;LEN=10485760;ID=BnF-MS-fr-2810;TIER=cold;AUTHORS=BnF;LICENSE=CC-BY-4.0;CHECKSUM=blake3:e3b0c4...|
```

### 4.5 Tag encoding

ASCII characters used in tags map to L1 bases via this lookup:

- ASCII byte → 8 bits → 4 bases (per §2.2)
- The special characters `|` (0x7C), `=` (0x3D), `;` (0x3B) are encoded normally.
- The encoder **MUST** ensure the tag does not violate L1 constraints (§2.3) by inserting padding bases between fields if necessary.

A conformant decoder identifies a tag by:
1. Scanning the start of an oligo for a 4-base pattern matching `|` (encoded as `GGCC`, since `|` = `0x7C` = `0b01111100`).
2. Decoding ASCII until a closing `|` is found.
3. Parsing key=value pairs separated by `;`.

### 4.6 Reserved key namespace

- Keys in lowercase are **reserved for implementation hints** (no compatibility guarantee).
- Keys starting with `x-` are **vendor extensions** (e.g. `x-microsoft-cluster=42`).
- Keys in UPPERCASE are **standardized** by this spec or its successors.

---

## 5. Layer 2 — Data Link (multiplexing) [v0.2 placeholder]

Layer 2 introduces multiplexing of multiple logical channels onto the same physical oligo. v0.1 reserves the design space; v0.2 will fully specify.

Planned mechanisms:

### 5.1 Strand multiplexing
- Forward strand decodes message A
- Reverse complement decodes message B
- Joint encoding via constraint solver

### 5.2 Reading frame multiplexing
- Frames 0, +1, +2 each decode independent messages
- Inspired by overlapping ORFs in phage PhiX174

### 5.3 Codec routing
- The L5 tag declares which L2 mode is active
- Decoder chooses correct reading direction/frame

---

## 6. Layer 3 — Network (random access) [v0.2 placeholder]

Layer 3 provides random-access semantics, allowing retrieval of specific blocks without reading the entire archive.

### 6.1 PCR primer index
- Each block is flanked by a unique 20-base PCR primer pair
- A primer-to-tag-ID index (the "filesystem table") is itself stored as a AeonScript block at a well-known primer address
- v0.2 will specify the index format

### 6.2 Hierarchical addressing
- Tags support hierarchical IDs (e.g. `BnF/manuscripts/MS-fr-2810`)
- Enables semantic queries like "retrieve all blocks where AUTHORS=BnF and TIER=cold"

---

## 7. Layer 6 — Presentation [v0.2 placeholder]

L6 covers:
- Compression (zstd, brotli, neural codecs)
- Encryption (AES-256-GCM, ChaCha20-Poly1305)
- Sérialisation des MIME types complexes

---

## 8. Layer 7 — Application [v0.2 placeholder]

L7 defines domain-specific extensions:

- **AeonScript-PDF** : PDF/A archival extension
- **AeonScript-FASTA** : direct biological sequence storage
- **AeonScript-Wiki** : Wikipedia article format
- **AeonScript-IIIF** : cultural heritage image format

---

## 9. Bio-safety protocol (cross-cutting, MANDATORY)

A **conformant** AeonScript encoder **MUST**, prior to outputting any oligo for synthesis :

1. Concatenate all output oligos into a candidate genome string.
2. Search the candidate against a hazard database. The minimum reference set is the **IGSC (International Gene Synthesis Consortium) Harmonized Screening Protocol** lookup.
3. If any match exceeding 20 base pairs at 90 % identity is found against pathogen-of-concern entries, the encoder **MUST** refuse to emit those oligos and **MUST** log the refusal.

A non-conformant encoder that bypasses this step **MUST NOT** label its output as "AeonScript-Compliant".

The hazard database is published separately at `<TBD>/aeonscript-hazard-db` and updated quarterly.

---

## 10. Versioning policy

- The spec follows **semantic versioning** : MAJOR.MINOR.PATCH.
- A change to a wire format → MAJOR bump.
- A new optional feature → MINOR bump.
- A clarification or fix → PATCH bump.
- A decoder **MUST** support the version it claims, and **SHOULD** support all earlier minor versions within the same major version.

---

## 11. Open questions for v0.2

1. Should the methylation hash be BLAKE3 or SHA-3-256? (BLAKE3 chosen tentatively for speed)
2. Optimal LDPC block geometry for typical oligo loss rates.
3. Standardized primer-pair vocabulary for PCR addressing (need ~10⁶ orthogonal pairs).
4. Compression interoperability with neural codecs (which neural codec to standardize?).
5. Multi-strand encoding constraint solver: greedy vs SAT-based vs neural-search.
6. Should the spec mandate a specific foundation model for AI-native encoding, or just a model-agnostic interface?

---

## 12. Acknowledgments

This specification builds on prior art including :

- Goldman et al. (2013) — early DNA storage encoding
- Erlich & Zielinski (2017) — DNA Fountain
- Press et al. (2020) — HEDGES error correction
- Microsoft Research / Karin Strauss et al. — cluster codec
- Brixi et al. (2026) — Evo 2 foundation model

We thank the broader DNA storage and bioinformatics communities for decades of foundational work.

---

*This is a living document. Comments and pull requests welcome at <TBD>/aeonscript.*
