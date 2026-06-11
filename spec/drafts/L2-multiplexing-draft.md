# AeonScript SPEC — Layer 2 (Multiplexing) — DRAFT for v0.2

**Status** : DRAFT. Not yet normative. Subject to substantial change.
**Targets** : v0.2 specification.
**Last updated** : 2026-06-07.

---

## 0. Why a Layer 2 at all

L1 (Physical) defines how *one* logical stream of bytes becomes a string of DNA bases. L2 (Data Link) defines how *multiple* logical streams can share the same physical strand.

This is exactly the biological situation in bacteriophages: PhiX174 packs eleven distinct proteins into ~5.3 kb by overlapping reading frames. The strand carries multiple messages depending on where the reader starts and which direction it travels.

Done right, L2 multiplexing can roughly double the effective density of an AeonScript block — going from ~1.4 bits utiles/base in v0.1 (L1+L5 only) toward ~2.5–3.0 bits/base in v0.2 (L1+L2+L5).

Done badly, L2 produces unsynthesisable DNA or unrecoverable data. The spec must constrain it tightly.

---

## 1. The three multiplexing mechanisms

L2 v0.2 defines three orthogonal multiplexing mechanisms. An implementation MAY use any subset; the L5 tag declares which are active.

### 1.1 Strand multiplexing (`L2-strand`)

The forward strand of an oligo decodes message A. The reverse complement of the same oligo decodes message B.

Conceptually:
```
forward 5'→3' :  ACGTAACGTAGCTAGCT...    → decodes to message A
reverse 5'→3' :  AGCTAGCTACGTTACGT...    → decodes to message B
(the second string is reverse complement of the first)
```

**Constraint** : the encoder must find a sequence such that *both* directions produce valid, decodable payloads. This is a constraint satisfaction problem (CSP).

**Capacity gain** : ~2× the data per base, minus the CSP overhead. Realistic estimate : 1.6×–1.8× depending on payload structure.

**Implementation hint** : split the joint encoding into 4-byte blocks. For each block, the forward bytes (4) and the reverse-complement-derived bytes (4) form an 8-byte joint search target. With per-byte permutations and a small dictionary of valid 4-byte patterns whose reverse complements are also valid, the search is tractable.

**Open question 1**: should `L2-strand` use a *symmetric* code (forward and reverse use the same codec) or *asymmetric* (different L4 profiles per direction)? The latter is more flexible but the L5 tag becomes more complex.

### 1.2 Reading-frame multiplexing (`L2-frame`)

The same forward strand is read at multiple offsets. Frame 0 (reading from position 0), Frame +1 (reading from position 1, skipping the first base), Frame +2 (position 2) all yield independent decodable payloads.

```
strand   : A C G T A C G T A C G T A C G T ...
frame 0  : [ACGT][ACGT][ACGT][ACGT]...        → message A
frame +1 : A[CGTA][CGTA][CGTA][CGTA]...        → message B  
frame +2 : AC[GTAC][GTAC][GTAC][GTAC]...        → message C
```

(With our 4-base-per-byte L1 mapping, only frames 0, +1, +2, +3 produce byte-aligned decodings — frame +4 = frame 0 shifted by one byte, which is just frame 0 starting one byte later.)

**Constraint** : same as strand multiplexing — bytes must satisfy all active frames simultaneously.

**Capacity gain** : up to 4× theoretically, but realistically 2×–2.5× because frame correlations sharply restrict the valid space.

**Implementation hint** : foundational genomic models (Evo 2, HyenaDNA) are *exceptionally* good at sequences that satisfy multiple-frame constraints — this is the bread and butter of overlapping ORF detection. The `L2-frame` codec is the most natural target for AI-native generation.

**Open question 2**: should the frame offset be encoded *physically* (as an offset of the permutation prefix) or *logically* (the L5 tag declares "this block uses frame 0+2", and the decoder applies the appropriate stride)? Logical is simpler; physical is more compact.

### 1.3 Codec routing (`L2-route`)

Multiple logical streams are interleaved at the block level — not at the bit level. Block N has L4 codec A; block N+1 has L4 codec B. The decoder uses each block's L5 tag to dispatch.

```
block 0 :  AEONSCRIPT=0.2;L4=rs255-223;...     ← classical RS
block 1 :  AEONSCRIPT=0.2;L4=evo2-v1;...       ← AI codec
block 2 :  AEONSCRIPT=0.2;L4=fountain;...      ← fountain code
...
```

This is the simplest mechanism — no joint encoding, no CSP — but it doesn't *increase* density per block. It allows **graceful codec migration**: an archive can mix old and new blocks indefinitely, because each block declares its own decoder.

This is what most "modern" file containers (Matroska, BMFF, EPUB) do. We adopt the pattern.

**Capacity gain** : zero on density, but enables *evolution* — which is the long-term archival win.

**Open question 3** : should the L5 tag declare a per-stream identifier (`STREAM=audio`, `STREAM=subtitles`) so a decoder can select streams without reading all blocks? Probably yes, but the tag syntax for stream IDs needs design.

---

## 2. Combinations and their constraints

The three mechanisms are orthogonal in principle but *constraints multiply* when combined.

| Mode | Density gain estimate | CSP complexity | AI-native gain |
|---|---|---|---|
| `L2-route` only | 1.0× | trivial | low |
| `L2-strand` only | ~1.7× | medium | medium |
| `L2-frame` only (3 frames) | ~2.4× | high | **very high** |
| `L2-strand` + `L2-route` | ~1.7× | medium | medium |
| `L2-strand` + `L2-frame` (3 frames) | ~3.8× theoretical | extreme | **highest** |
| `L2-strand` + `L2-frame` (4 frames) | ~5.2× theoretical | borderline-infeasible without AI | only feasible with AI |

The highest combinations are exactly where foundation models earn their density. v0.2 will mandate that any implementation using `L2-strand` + `L2-frame ≥ 2` declare a `L2-codec` profile (either `algorithmic-csp-v1` or `evo2-v1` etc.) so decoders know how the joint encoding was searched.

---

## 3. Wire format additions

### 3.1 New L5 tag keys

```
L2 = L2-strand,L2-frame=0+2,L2-route   # comma-separated active mechanisms
L2-codec = algorithmic-csp-v1          # how the joint encoding was searched
L2-frames = 0,2                         # which frames carry data when L2-frame is active
L2-strand-target = primary             # primary | reverse (for L2-strand)
STREAM = identifier-for-multiplexed-streams
```

### 3.2 Backwards compatibility

A v0.1 decoder reading a v0.2 block:
- Sees `AEONSCRIPT=0.2`, knows it can't fully decode
- Sees `L2=L2-strand` and refuses (or attempts forward-only and emits a warning)

A v0.2 decoder reading a v0.1 block:
- Sees `AEONSCRIPT=0.1`, sees no `L2` key
- Defaults to `L2=none` → backward-compatible decode

### 3.3 Decoder dispatch pseudocode

```python
def decode(oligos):
    tag = parse_tag(strip_scrambler(oligos_to_bytes(oligos)))
    if tag["AEONSCRIPT"] != "0.2":
        ...  # raise or downgrade
    
    active_l2 = tag.get("L2", "none").split(",")
    
    if "L2-strand" in active_l2:
        payload_fwd = decode_with_l4(tag["L4"], scrambler_bytes)
        payload_rev = decode_with_l4(tag["L4"], reverse_complement(scrambler_bytes))
    
    if "L2-frame" in active_l2:
        for offset in tag["L2-frames"].split(","):
            payload_n = decode_with_l4(tag["L4"], scrambler_bytes[offset:])
    
    if "L2-route" in active_l2:
        for block_n in blocks_in_archive:
            dispatch_by_codec(block_n.tag["L4"])
    
    return assemble(payload_fwd, payload_rev, payload_n, ...)
```

---

## 4. Constraint solver requirements

For `L2-strand` and `L2-frame`, the encoder must search for sequences satisfying all active constraints simultaneously.

### 4.1 Required CSP capabilities

A conformant v0.2 implementation MUST be able to:

1. Enumerate candidate sequences for a target payload byte-stream.
2. For each candidate, verify all active L2 constraints.
3. Either accept the first valid candidate or use a search procedure (greedy / SAT / neural) to find one.

The spec does NOT mandate a specific search algorithm. v0.2 ships:
- A reference greedy implementation (slow, ~kb/s)
- A reference SAT implementation (medium, ~10 kb/s)
- A reference neural implementation hook (Evo 2, fast at scale)

### 4.2 Search budget

Each block has a **search budget** — maximum CSP attempts before the encoder gives up and re-segments the payload. Default budget: 10⁵ candidates per oligo.

If the encoder exceeds the budget without finding a valid sequence, it MUST:
- Either reduce the L2 ambition (drop a multiplexing mechanism for this block)
- Or split the payload into smaller blocks

This is documented in the L5 tag as `L2-RELAXATIONS=dropped-strand-on-block-42` (TBD syntax).

---

## 5. Test vector requirements

For v0.2, test vectors will be substantially more complex than v0.1. Each vector will include:

```json
{
  "id": "tv-L2-strand-01",
  "input": {
    "payload_fwd_hex": "...",
    "payload_rev_hex": "...",
    "block_id": "...",
    "mime_type": "..."
  },
  "expected": {
    "l5_tag": "|AEONSCRIPT=0.2;L1=L1-4;L4=rs255-223;L2=L2-strand;...|",
    "oligos": ["..."],
    "verification": {
      "fwd_decode_payload": "...",  // matches input.payload_fwd_hex
      "rev_decode_payload": "..."  // matches input.payload_rev_hex
    }
  }
}
```

A conformant L2-strand encoder MUST produce oligos whose forward decode yields `payload_fwd_hex` AND whose reverse-complement decode yields `payload_rev_hex`.

---

## 6. Bio-safety implications

`L2-frame` and `L2-strand` increase the surface area of bio-safety screening. A sequence that is safe when read in one direction may match a hazard signature when read in the other, or in a shifted frame.

A conformant `L2-{strand,frame}` encoder MUST screen the oligo in **all active multiplex configurations** against the hazard database, not just the primary configuration.

Concretely: the `enforce_biosafety()` API gains a new parameter:

```python
enforce_biosafety(
    oligos,
    multiplex_modes=["forward", "reverse", "frame+1", "frame+2"]
)
```

---

## 7. Open questions for v0.2 RFC

These are the design decisions that need community input before v0.2 freezes:

1. **L2-strand symmetry**: same codec per direction, or asymmetric?
2. **L2-frame offset encoding**: physical (prefix) or logical (tag declaration)?
3. **Stream identifiers**: how to name multiplexed logical streams?
4. **Search budget**: per-block, or global?
5. **CSP profile registration**: should `L2-codec` be open-vocabulary or registered-only?
6. **Mixed-direction hazards**: how to express "this sequence is safe forward but unsafe reverse"?
7. **AI-native codecs**: should the spec mandate a specific model (Evo 2) or just an interface?
8. **Density target**: should v0.2 normatively target 2.5 bits/base, or remain implementation-defined?

---

## 8. Migration plan from v0.1 to v0.2

v0.2 will be a SemVer-MINOR release relative to v0.1 (both belong to the 0.x development series). Concretely:

- **Backwards compatible**: v0.1 blocks remain decodable by v0.2 decoders.
- **Forwards incompatible**: v0.2 blocks are NOT decodable by v0.1-only decoders. They explicitly declare `AEONSCRIPT=0.2`.
- **Reference codec**: the Python `aeonscript` package will gain new modules (`aeonscript.l2`, `aeonscript.csp`) without changing the v0.1 API.
- **Conformance**: a Level-1 v0.2 implementation must also be Level-1 v0.1 conformant. The vectors are additive.

---

## 9. What this draft is NOT

This draft is **not** a normative spec. It describes the design space and the constraints. The final v0.2 spec will:

- Pick one option for each open question (typically the simplest)
- Define exact wire format byte patterns
- Provide a reference implementation that compiles and runs
- Ship test vectors that any implementation must reproduce

The point of releasing this draft now is to get community feedback on the design choices *before* they freeze. Open a discussion or issue at https://github.com/aeonscript-spec/aeonscript/discussions.

---

## 10. Acknowledgements

Conceptual inspiration:

- **PhiX174 phage** — biology's own demonstration of overlapping reading frames at scale
- **Caduceus / HyenaDNA / Evo 2** — foundation models capable of learning multi-frame constraints
- **OSI Layer 2 (Data Link)** — the conceptual analogue for "multiple logical streams over one physical medium"
- **Matroska / EBML** — the open-vocabulary container format that inspired `L2-route`

If you're working on any of these and want to shape the v0.2 spec, please reach out via [Discussions](https://github.com/aeonscript-spec/aeonscript/discussions).
