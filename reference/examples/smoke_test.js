/**
 * AeonScript L1+L5 smoke test (Node.js).
 *
 * Mirror of physical.py + semantic.py for environments without Python.
 * Demonstrates that the AeonScript encoding mechanism round-trips correctly.
 * Does NOT include Reed-Solomon (L4) — for that, run the Python reference.
 *
 * Usage:
 *   node smoke_test.js
 */

"use strict";

// ---------------------------------------------------------------------------
// L1 — Physical layer (port of physical.py)
// ---------------------------------------------------------------------------

const BASE_PERMUTATIONS = [
  ["A", "C", "G", "T"],
  ["A", "G", "C", "T"],
  ["T", "C", "G", "A"],
  ["C", "A", "T", "G"],
  ["G", "T", "A", "C"],
];
const PREFIX_CODES = ["ACGT", "AGCT", "TCGA", "CATG", "GTAC"];
// v0.1 reference uses RELAXED constraints matching industrial synthesis tolerance.
// A constraint-tight codec (Goldman ternary / RLL) is on the v0.2 roadmap.
const FORBIDDEN_MOTIFS = ["GGGGGGGGGGGGG", "ATATATATATATAT"];
const MAX_HOMOPOLYMER = 10;
const GC_MIN = 0.20;
const GC_MAX = 0.80;

function byteToBases(byte, perm) {
  const out = [];
  for (const shift of [0, 2, 4, 6]) {
    out.push(perm[(byte >> shift) & 0b11]);
  }
  return out.join("");
}

function basesToByte(bases, perm) {
  const inv = {};
  perm.forEach((b, i) => (inv[b] = i));
  let value = 0;
  for (let i = 0; i < 4; i++) {
    value |= inv[bases[i]] << (2 * i);
  }
  return value;
}

function constraintViolation(seq) {
  let run = 1, maxRun = 1, maxRunBase = seq[0];
  for (let i = 1; i < seq.length; i++) {
    if (seq[i] === seq[i - 1]) {
      run++;
      if (run > maxRun) { maxRun = run; maxRunBase = seq[i]; }
    } else run = 1;
  }
  if (maxRun > MAX_HOMOPOLYMER) return `homopolymer ${maxRunBase}×${maxRun}`;
  for (const motif of FORBIDDEN_MOTIFS) {
    if (seq.includes(motif)) return `motif ${motif}`;
  }
  if (seq.length >= 10) {
    let gc = 0;
    for (const b of seq) if (b === "G" || b === "C") gc++;
    const ratio = gc / seq.length;
    if (ratio < GC_MIN) return `GC% ${(ratio*100).toFixed(1)} < ${(GC_MIN*100).toFixed(0)}`;
    if (ratio > GC_MAX) return `GC% ${(ratio*100).toFixed(1)} > ${(GC_MAX*100).toFixed(0)}`;
  }
  return null;
}
function violatesConstraints(seq) { return constraintViolation(seq) !== null; }

function bytesToDna(data) {
  const failures = [];
  for (let i = 0; i < BASE_PERMUTATIONS.length; i++) {
    const perm = BASE_PERMUTATIONS[i];
    let body = "";
    for (const byte of data) body += byteToBases(byte, perm);
    const candidate = PREFIX_CODES[i] + body;
    const v = constraintViolation(candidate);
    if (v === null) return candidate;
    failures.push(`perm${i}: ${v}`);
  }
  throw new Error(`All permutations violate L1: [${failures.join(" | ")}]\n  chunk hex: ${Buffer.from(data).toString("hex").slice(0, 80)}...`);
}

function dnaToBytes(seq) {
  if (seq.length < 4 || (seq.length - 4) % 4 !== 0) {
    throw new Error(`Invalid sequence length: ${seq.length}`);
  }
  const prefix = seq.slice(0, 4);
  const body = seq.slice(4);
  const permIdx = PREFIX_CODES.indexOf(prefix);
  if (permIdx < 0) throw new Error(`Unknown prefix: ${prefix}`);
  const perm = BASE_PERMUTATIONS[permIdx];
  const out = Buffer.alloc(body.length / 4);
  for (let i = 0; i < body.length; i += 4) {
    out[i / 4] = basesToByte(body.slice(i, i + 4), perm);
  }
  return out;
}

// ---------------------------------------------------------------------------
// Scrambler — xorshift32 PRBS to uniformize byte distribution
// Standard technique in DNA storage codecs to balance GC and avoid runs.
// ---------------------------------------------------------------------------

const SCRAMBLER_SEED = 0xDEADBEEF;

function scramble(data, seedOffset = 0) {
  let state = (SCRAMBLER_SEED ^ seedOffset) >>> 0;
  const out = Buffer.alloc(data.length);
  for (let i = 0; i < data.length; i++) {
    state ^= (state << 13) >>> 0; state >>>= 0;
    state ^= state >>> 17;
    state ^= (state << 5) >>> 0; state >>>= 0;
    out[i] = data[i] ^ (state & 0xFF);
  }
  return out;
}
const descramble = scramble; // XOR is self-inverse

// ---------------------------------------------------------------------------
// L5 — Semantic tags (port of semantic.py)
// ---------------------------------------------------------------------------

function makeTag(opts) {
  const fields = {
    AEONSCRIPT: opts.specVersion || "0.1",
    L1: opts.l1Profile || "L1-4",
    L4: opts.l4Codec || "none",
    TYPE: opts.mimeType || "application/octet-stream",
    LEN: String(opts.payloadLen),
    ID: opts.blockId,
    ...(opts.optional || {}),
  };
  const body = Object.entries(fields)
    .map(([k, v]) => `${k}=${v}`)
    .join(";");
  return `|${body}|`;
}

function parseTag(tag) {
  if (!tag.startsWith("|") || !tag.endsWith("|")) {
    throw new Error(`Malformed tag: ${tag.slice(0, 80)}`);
  }
  const body = tag.slice(1, -1);
  const out = {};
  for (const pair of body.split(";")) {
    const eq = pair.indexOf("=");
    if (eq < 0) throw new Error(`Malformed field: ${pair}`);
    out[pair.slice(0, eq)] = pair.slice(eq + 1);
  }
  return out;
}

// ---------------------------------------------------------------------------
// High-level demo (L1 + L5 only, no Reed-Solomon for this smoke test)
// ---------------------------------------------------------------------------

function encodeBytes(data, mimeType, blockId) {
  const tag = makeTag({
    mimeType,
    blockId,
    payloadLen: data.length,
  });
  // Scramble the ENTIRE stream (tag + data) to balance GC and break biases.
  // The decoder descrambles first, then parses the tag from descrambled bytes.
  const plain = Buffer.concat([Buffer.from(tag, "ascii"), data]);
  const stream = scramble(plain);

  const OLIGO_LEN = 200;
  const bytesPerOligo = Math.floor((OLIGO_LEN - 4) / 4);
  const oligos = [];
  for (let i = 0; i < stream.length; i += bytesPerOligo) {
    oligos.push(bytesToDna(stream.slice(i, i + bytesPerOligo)));
  }
  return oligos;
}

function decodeOligos(oligos) {
  const scrambled = Buffer.concat(oligos.map(dnaToBytes));
  const plain = descramble(scrambled);
  if (plain[0] !== 0x7c /* | */) throw new Error("Descrambled stream does not start with tag");
  const end = plain.indexOf(0x7c, 1);
  const tag = parseTag(plain.slice(0, end + 1).toString("ascii"));
  const payload = plain.slice(end + 1, end + 1 + parseInt(tag.LEN, 10));
  return { payload, tag };
}

// ---------------------------------------------------------------------------
// Run
// ---------------------------------------------------------------------------

const banner = (s) => {
  console.log("\n" + "=".repeat(70));
  console.log("  " + s);
  console.log("=".repeat(70));
};

const PASSAGE = Buffer.from(
  "« La mémoire de l'humanité ne devrait pas être propriétaire. »\n\n" +
    "Test smoke L1+L5 du codec AeonScript en Node.js. " +
    "Si vous lisez ceci, l'encodage ADN -> bytes a round-trippé correctement.",
  "utf-8"
);

banner("AeonScript Node.js Smoke Test — Encode");
console.log(`Original payload: ${PASSAGE.length} bytes`);

const oligos = encodeBytes(PASSAGE, "text/plain", "smoke-1");
const totalBases = oligos.reduce((s, o) => s + o.length, 0);
console.log(`Encoded into ${oligos.length} oligos, total ${totalBases} bases`);
console.log(`Density: ${(PASSAGE.length * 8 / totalBases).toFixed(3)} bits/base (no RS in this test)`);

banner("Sample oligos");
oligos.slice(0, 3).forEach((o, i) =>
  console.log(`  [${i}] (${o.length}b) ${o.slice(0, 60)}${o.length > 60 ? "…" : ""}`)
);

banner("Round-trip decode");
const { payload, tag } = decodeOligos(oligos);
const ok = payload.equals(PASSAGE);
console.log(ok ? "  ✓ Round-trip OK — bytes identical" : "  ✗ MISMATCH");
console.log("  Parsed tag:");
for (const [k, v] of Object.entries(tag)) console.log(`    ${k.padEnd(10)} = ${v}`);

banner("Constraint verification");
let ctrOk = 0, ctrBad = 0;
for (const o of oligos) {
  // Quick constraint re-check
  const gc = [...o].filter((b) => b === "G" || b === "C").length / o.length;
  let maxRun = 1, cur = 1;
  for (let i = 1; i < o.length; i++) {
    if (o[i] === o[i - 1]) { cur++; maxRun = Math.max(maxRun, cur); }
    else cur = 1;
  }
  if (maxRun <= 10 && gc >= 0.20 && gc <= 0.80) ctrOk++;
  else ctrBad++;
}
console.log(`  Constraint-compliant oligos: ${ctrOk}/${oligos.length}`);
if (ctrBad > 0) console.log(`  ⚠ ${ctrBad} oligos violate constraints (encoder bug)`);

banner("Done");
console.log("  L1 + L5 round-trip verified in Node.js.");
console.log("  Full L4 (Reed-Solomon error correction) tested via Python reference.");
process.exit(ok && ctrBad === 0 ? 0 : 1);
