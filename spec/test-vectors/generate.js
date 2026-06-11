/**
 * Generate canonical test vectors for AeonScript L1+L5 conformance.
 *
 * Reads test inputs from this file, runs the reference Node smoke-test
 * encoder, and emits JSON test vectors that any conformant implementation
 * MUST reproduce identically.
 *
 * NB: these vectors cover L1+L5 only (no Reed-Solomon). L4 vectors with
 * RS parity bytes are generated from the Python reference (which uses the
 * `reedsolo` library), see vectors-l1-l4-l5.json.
 *
 * Run:
 *   node spec/test-vectors/generate.js
 */

"use strict";

const fs = require("fs");
const path = require("path");

// ---------------------------------------------------------------------------
// Mirror of reference/examples/smoke_test.js — kept in sync manually.
// (Both files use exactly the same algorithms.)
// ---------------------------------------------------------------------------

const BASE_PERMUTATIONS = [
  ["A", "C", "G", "T"],
  ["A", "G", "C", "T"],
  ["T", "C", "G", "A"],
  ["C", "A", "T", "G"],
  ["G", "T", "A", "C"],
];
const PREFIX_CODES = ["ACGT", "AGCT", "TCGA", "CATG", "GTAC"];
const FORBIDDEN_MOTIFS = ["GGGGGGGGGGGGG", "ATATATATATATAT"];
const MAX_HOMOPOLYMER = 10;
const GC_MIN = 0.20;
const GC_MAX = 0.80;
const SCRAMBLER_SEED = 0xDEADBEEF;

function byteToBases(byte, perm) {
  return [0,2,4,6].map(s => perm[(byte >> s) & 0b11]).join("");
}
function basesToByte(bases, perm) {
  const inv = {}; perm.forEach((b,i)=>inv[b]=i);
  let v = 0;
  for (let i = 0; i < 4; i++) v |= inv[bases[i]] << (2*i);
  return v;
}
function violates(seq) {
  let run = 1;
  for (let i = 1; i < seq.length; i++) {
    if (seq[i] === seq[i-1]) { run++; if (run > MAX_HOMOPOLYMER) return true; }
    else run = 1;
  }
  for (const m of FORBIDDEN_MOTIFS) if (seq.includes(m)) return true;
  if (seq.length >= 10) {
    const gc = [...seq].filter(b => b==="G"||b==="C").length / seq.length;
    if (gc < GC_MIN || gc > GC_MAX) return true;
  }
  return false;
}
function bytesToDna(data) {
  for (let i = 0; i < BASE_PERMUTATIONS.length; i++) {
    let body = "";
    for (const b of data) body += byteToBases(b, BASE_PERMUTATIONS[i]);
    const candidate = PREFIX_CODES[i] + body;
    if (!violates(candidate)) return candidate;
  }
  throw new Error("L1 constraints not satisfiable");
}
function dnaToBytes(seq) {
  const permIdx = PREFIX_CODES.indexOf(seq.slice(0,4));
  if (permIdx < 0) throw new Error(`Unknown prefix: ${seq.slice(0,4)}`);
  const perm = BASE_PERMUTATIONS[permIdx];
  const body = seq.slice(4);
  const out = Buffer.alloc(body.length / 4);
  for (let i = 0; i < body.length; i += 4) {
    out[i/4] = basesToByte(body.slice(i, i+4), perm);
  }
  return out;
}
function scramble(data) {
  let state = SCRAMBLER_SEED >>> 0;
  const out = Buffer.alloc(data.length);
  for (let i = 0; i < data.length; i++) {
    state ^= (state << 13) >>> 0; state >>>= 0;
    state ^= state >>> 17;
    state ^= (state << 5) >>> 0; state >>>= 0;
    out[i] = data[i] ^ (state & 0xFF);
  }
  return out;
}
function makeTag(payload, blockId, mime) {
  return `|AEONSCRIPT=0.1;L1=L1-4;L4=none;TYPE=${mime};LEN=${payload.length};ID=${blockId}|`;
}
function encodeL1L5(payload, blockId, mime) {
  const tag = makeTag(payload, blockId, mime);
  const stream = scramble(Buffer.concat([Buffer.from(tag, "ascii"), payload]));
  const OLIGO_LEN = 200;
  const bytesPerOligo = Math.floor((OLIGO_LEN - 4) / 4);
  const oligos = [];
  for (let i = 0; i < stream.length; i += bytesPerOligo) {
    oligos.push(bytesToDna(stream.slice(i, i + bytesPerOligo)));
  }
  return { tag, oligos };
}

// ---------------------------------------------------------------------------
// Canonical test inputs
// ---------------------------------------------------------------------------

const TEST_INPUTS = [
  { id: "tv-01-empty",       payload: "",                                    mime: "application/octet-stream" },
  { id: "tv-02-ascii-short", payload: "Hello, AeonScript.",                  mime: "text/plain" },
  { id: "tv-03-ascii-long",  payload: "The quick brown fox jumps over the lazy dog. ".repeat(4), mime: "text/plain" },
  { id: "tv-04-binary",      payload: Buffer.from([...Array(64)].map((_,i) => i)).toString("binary"), mime: "application/octet-stream" },
  { id: "tv-05-all-zeros",   payload: "\x00".repeat(32),                    mime: "application/octet-stream" },
  { id: "tv-06-all-ones",    payload: "\xff".repeat(32),                    mime: "application/octet-stream" },
  { id: "tv-07-utf8",        payload: "Hélix ADN — archive millénaire.",     mime: "text/plain" },
  { id: "tv-08-json",        payload: '{"name":"aeonscript","v":"0.1"}',     mime: "application/json" },
  { id: "tv-09-emoji",       payload: "🧬 📜 🔬 ✨",                          mime: "text/plain" },
  { id: "tv-10-medium",      payload: "abcdefghijklmnopqrstuvwxyz0123456789".repeat(8), mime: "text/plain" },
];

const vectors = TEST_INPUTS.map((tv) => {
  const payload = tv.payload.includes("\\") || /[\x00-\x1f\x7f-\xff]/.test(tv.payload)
    ? Buffer.from(tv.payload, "binary")
    : Buffer.from(tv.payload, "utf-8");
  const { tag, oligos } = encodeL1L5(payload, tv.id, tv.mime);
  return {
    id: tv.id,
    description: `Canonical test vector: ${tv.id}`,
    input: {
      payload_hex: payload.toString("hex"),
      payload_len_bytes: payload.length,
      block_id: tv.id,
      mime_type: tv.mime,
    },
    expected: {
      l5_tag_ascii: tag,
      l1_profile: "L1-4",
      l4_codec: "none",
      oligo_count: oligos.length,
      total_bases: oligos.reduce((s,o) => s + o.length, 0),
      oligos: oligos,
    },
  };
});

// ---------------------------------------------------------------------------
// Write to disk
// ---------------------------------------------------------------------------

const output = {
  schema_version: "1.0",
  generator: "aeonscript/spec/test-vectors/generate.js",
  generated_at: "2026-06-07T00:00:00Z",
  spec_version: "0.1",
  l1_profile: "L1-4",
  l4_codec: "none",
  scrambler: { algorithm: "xorshift32", seed_hex: "deadbeef" },
  oligo_length_target_bases: 200,
  notes: [
    "These vectors cover L1 (physical) + L5 (semantic tag) only.",
    "L4 (Reed-Solomon) vectors are generated separately from the Python reference.",
    "Every conformant L1-4 encoder MUST reproduce these oligos byte-for-byte.",
    "The decoder MUST round-trip each input through the oligos back to the payload.",
  ],
  vectors,
};

const outPath = path.join(__dirname, "vectors-l1-l5.json");
fs.writeFileSync(outPath, JSON.stringify(output, null, 2));
console.log(`Wrote ${vectors.length} vectors to ${outPath}`);
console.log(`Total: ${output.vectors.reduce((s,v) => s + v.expected.total_bases, 0)} bases across all vectors`);
