# Glossary

AeonScript sits at the intersection of biology, information theory, and software. This glossary makes that vocabulary accessible from either side.

---

## Biology / DNA

**A, C, G, T** — the four nucleotide bases of DNA: adenine, cytosine, guanine, thymine. A pairs with T; G pairs with C.

**Base** — a single nucleotide. In AeonScript, the smallest unit of information on a strand.

**Bioinformatics** — computational analysis of biological data (DNA, RNA, protein sequences).

**bp** — base pair. The length unit for DNA: 1 bp = one base on each of two complementary strands.

**CDS** — coding sequence. A region of DNA that codes for a protein.

**Codon** — a group of 3 consecutive bases that codes for one amino acid in the genetic code. AeonScript does *not* use codons; we encode binary data, not amino acids.

**Complementary strand** (reverse complement) — the strand pairing with a given DNA strand. If forward reads `ACGT`, the reverse complement reads `ACGT` (because A↔T and C↔G, then reversed).

**dNaM / d5SICS / dTPT3** — unnatural nucleotides synthesized for expanded genetic alphabets (e.g. Romesberg lab, Synthorx). Future L1 profiles may use these.

**DNA storage** — the practice of encoding arbitrary digital data onto synthetic DNA, then reading it back via sequencing. Distinct from biological gene expression.

**GC content** — percentage of bases in a sequence that are G or C. Synthesis and sequencing both require GC content in a specific range (typically 40–60%, AeonScript v0.1 relaxes to 25–75%).

**Helix** — the iconic double-stranded shape DNA naturally takes.

**Homopolymer** — a run of identical bases (e.g. `AAAA`). Long homopolymers (typically > 6–10) confuse sequencing technologies. AeonScript v0.1 limits runs to ≤ 8.

**IGSC** — International Gene Synthesis Consortium. A coalition of synthesis vendors with a harmonized screening protocol to detect dangerous sequences. Referenced in SPEC §9.

**Methylation** — chemical addition of a methyl group (`-CH₃`) to a base. 5-methylcytosine (5mC) is the most common; readable by Nanopore sequencing. Future L1 profile `L1-5m` will use it as a fifth symbol.

**Nanopore** — sequencing technology (Oxford Nanopore) that reads bases as they pass through a tiny pore. Can detect methylated bases natively.

**Nucleotide** — synonym for "base" in this context.

**Oligo / oligonucleotide** — a short synthesized DNA sequence (typically 100–300 bases). AeonScript blocks are stored as collections of oligos.

**ORF** — open reading frame. A region of DNA that *could* code for a protein. Not relevant to AeonScript directly but referenced in §5.2 of the spec (multiplexed reading frames).

**PCR** — polymerase chain reaction. A technique for selectively amplifying a specific DNA sequence. Used in DNA storage to retrieve specific oligos via primer-based addressing (L3).

**Primer** — a short DNA sequence (~20 bases) used to mark and selectively amplify a region of DNA. AeonScript L3 will use PCR primers as block addresses.

**Synthesis** — manufacturing DNA from scratch (chemical or enzymatic). The current bottleneck for DNA storage economics.

**Sequencing** — reading existing DNA. Mature technology (Illumina, Nanopore, PacBio).

**5mC, 5hmC** — 5-methylcytosine, 5-hydroxymethylcytosine. Modified cytosines used as extra symbols in extended L1 profiles.

---

## Information theory

**Bit** — fundamental unit of information (0 or 1). AeonScript encodes 2 bits per DNA base in the canonical L1-4 profile.

**Channel** — abstract medium that transmits information with some error probability. DNA is the channel here.

**Codec** — encoder + decoder pair. AeonScript v0.1 is one codec; we hope many implementations exist.

**Codeword** — the output of an error-correcting code: data + parity. RS(255, 223) means each codeword is 255 bytes (223 data + 32 parity).

**Compression** — removing redundancy from data to reduce size. Different from error-correction (which *adds* redundancy).

**Erasure** — a known-missing symbol. Easier to correct than unknown errors. RS can recover twice as many erasures as errors.

**Error correction** (FEC, forward error correction) — adding redundancy so the receiver can recover from corruption without re-transmission. Reed-Solomon, LDPC, fountain codes are common.

**GF(256)** — Galois Field of 256 elements. The arithmetic system Reed-Solomon operates over. Each element is a byte.

**LDPC** — Low-Density Parity-Check. A modern error-correcting code, used in 5G and Wi-Fi. AeonScript L4 v0.2 will use LDPC as outer code.

**Pseudo-random binary sequence (PRBS)** — a deterministic stream that looks random. Used by AeonScript as a *scrambler* to balance GC content without adding entropy.

**Reed-Solomon (RS)** — classic error-correcting code (Reed & Solomon 1960). Used in CD audio, QR codes, satellite links. RS(n, k) encodes k data bytes into n bytes with (n−k)/2 errors correctable. AeonScript uses RS(255, 223) → corrects up to 16 errors per 255-byte codeword.

**Run-length-limited (RLL)** — encodings that bound the maximum run of identical symbols. Common in magnetic storage. Future AeonScript L1 profiles will use RLL.

**Shannon limit** — the theoretical maximum information rate of a channel. For DNA, that's 2 bits/base in the simplest model. Real codecs achieve ~70–90% of this due to constraints.

**Wire format** — the on-the-wire (or "on-the-strand") byte/base representation of a structured message.

---

## Software / standards

**API** — Application Programming Interface. The functions an implementation exposes to callers.

**CC-BY-SA** — Creative Commons Attribution-ShareAlike. The license used for AeonScript documentation. Derivative works must remain under the same license.

**Conformance** — formal property that an implementation correctly follows the spec. See [CONFORMANCE.md](../spec/CONFORMANCE.md).

**FAQ** — Frequently Asked Questions. See [FAQ.md](../FAQ.md).

**MIT** — permissive software license. Used for AeonScript code. Allows commercial use, modification, redistribution.

**Normative** — describing requirements that MUST be followed by conformant implementations. RFC 2119 keywords (MUST, SHOULD, MAY) mark normative text.

**OSI model** — 7-layer reference architecture for networking. AeonScript borrows the layered structure but maps it to DNA storage.

**RFC 2119** — IETF document defining "MUST", "SHOULD", "MAY" in standards.

**Test vector** — a canonical input/output pair that conformant implementations MUST reproduce.

---

## AeonScript-specific terms

**Block** — a unit of storage that is independently addressable. One block = one L5 tag + payload + parity.

**L1, L2, ..., L7** — the seven layers of the AeonScript architecture. See [SPEC](../spec/SPEC-v0.1.md).

**L1 profile** — variant of the physical layer. `L1-4` uses 4 symbols (A,C,G,T), `L1-5m` uses 5 (adds 5mC), `L1-6` uses 6.

**Permutation prefix** — a 4-base sequence at the start of each oligo that tells the decoder which `{A,C,G,T}↔{00,01,10,11}` mapping the rest of the oligo uses. AeonScript v0.1 tries up to 5 permutations to satisfy biochemical constraints.

**Phylogenetic tag** — *(not used in AeonScript)* — in genomic foundation models (like Evo 2), a metadata string identifying species. AeonScript's semantic tag serves a different purpose.

**Scrambler** — the xorshift32 PRBS that XORs the stream before L1 encoding, to balance GC content.

**Semantic tag** — the `|AEONSCRIPT=0.1;L1=L1-4;TYPE=...|` prefix at the start of each block. Makes the file self-describing.

**Self-describing** — every block carries its own codec version, so it can be decoded without external context.

---

*Missing a term? [Open an issue](https://github.com/aeonscript-spec/aeonscript/issues) and we'll add it.*
