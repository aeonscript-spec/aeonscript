//! Layer 1 — Physical: binary ↔ DNA encoding under biochemical constraints.
//!
//! Mirrors `reference/aeonscript/physical.py`. Byte-compatible with the
//! Python and Node references on the canonical test vectors.
//!
//! v0.1 reference uses the L1-4 profile: 2 bits per base, with a 4-base
//! permutation prefix per oligo to keep individual oligos within
//! synthesis-friendly biochemical bounds.

const BASE_PERMUTATIONS: [[char; 4]; 5] = [
    ['A', 'C', 'G', 'T'],
    ['A', 'G', 'C', 'T'],
    ['T', 'C', 'G', 'A'],
    ['C', 'A', 'T', 'G'],
    ['G', 'T', 'A', 'C'],
];

const PREFIX_CODES: [&str; 5] = ["ACGT", "AGCT", "TCGA", "CATG", "GTAC"];

const FORBIDDEN_MOTIFS: &[&str] = &["GGGGGGGGGGGGG", "ATATATATATATAT"];
const MAX_HOMOPOLYMER: usize = 10;
const GC_MIN: f64 = 0.20;
const GC_MAX: f64 = 0.80;

/// Errors produced by the L1 codec.
#[derive(Debug, thiserror::Error)]
#[allow(missing_docs)]
pub enum PhysicalError {
    #[error("All permutations violate L1 constraints — this is rare for scrambled input")]
    ConstraintsUnsatisfiable,
    #[error("Sequence too short to contain a permutation prefix")]
    SequenceTooShort,
    #[error("Sequence body length must be a multiple of 4 bases (got {0} after prefix)")]
    InvalidBodyLength(usize),
    #[error("Unknown permutation prefix: {0:?}")]
    UnknownPrefix(String),
    #[error("Unknown base in sequence: {0:?}")]
    UnknownBase(char),
}

/// Encode a single byte as 4 DNA bases using the given permutation.
/// LSB-first within the byte.
fn byte_to_bases(byte: u8, perm: &[char; 4]) -> String {
    let mut out = String::with_capacity(4);
    for shift in &[0, 2, 4, 6] {
        let code = ((byte >> shift) & 0b11) as usize;
        out.push(perm[code]);
    }
    out
}

/// Decode 4 DNA bases back to a single byte using the given permutation.
fn bases_to_byte(bases: &[char], perm: &[char; 4]) -> Result<u8, PhysicalError> {
    if bases.len() != 4 {
        return Err(PhysicalError::InvalidBodyLength(bases.len()));
    }
    let mut value: u8 = 0;
    for (i, &b) in bases.iter().enumerate() {
        let pos = perm
            .iter()
            .position(|&p| p == b)
            .ok_or(PhysicalError::UnknownBase(b))?;
        value |= (pos as u8) << (2 * i as u8);
    }
    Ok(value)
}

/// Return true if the candidate sequence violates an L1 biochemical
/// constraint (homopolymer run, GC range, forbidden motif).
fn violates_constraints(seq: &str) -> bool {
    // Homopolymer run length
    let chars: Vec<char> = seq.chars().collect();
    let mut run = 1usize;
    for i in 1..chars.len() {
        if chars[i] == chars[i - 1] {
            run += 1;
            if run > MAX_HOMOPOLYMER {
                return true;
            }
        } else {
            run = 1;
        }
    }
    // Forbidden motifs
    for motif in FORBIDDEN_MOTIFS {
        if seq.contains(*motif) {
            return true;
        }
    }
    // GC content
    if chars.len() >= 10 {
        let gc = chars
            .iter()
            .filter(|&&c| c == 'G' || c == 'C')
            .count() as f64;
        let ratio = gc / chars.len() as f64;
        if !(GC_MIN..=GC_MAX).contains(&ratio) {
            return true;
        }
    }
    false
}

/// Encode arbitrary bytes as a DNA sequence respecting L1 constraints.
///
/// Tries each base permutation in turn until biochemical constraints are
/// satisfied. Returns the DNA sequence including the 4-base permutation
/// prefix.
///
/// In practice, given the upstream scrambler produces a uniform byte
/// distribution, the first permutation almost always succeeds.
pub fn bytes_to_dna(data: &[u8]) -> Result<String, PhysicalError> {
    for (perm_idx, perm) in BASE_PERMUTATIONS.iter().enumerate() {
        let mut body = String::with_capacity(data.len() * 4);
        for &b in data {
            body.push_str(&byte_to_bases(b, perm));
        }
        let candidate = format!("{}{}", PREFIX_CODES[perm_idx], body);
        if !violates_constraints(&candidate) {
            return Ok(candidate);
        }
    }
    Err(PhysicalError::ConstraintsUnsatisfiable)
}

/// Decode a DNA sequence (with permutation prefix) back to bytes.
pub fn dna_to_bytes(seq: &str) -> Result<Vec<u8>, PhysicalError> {
    if seq.len() < 4 {
        return Err(PhysicalError::SequenceTooShort);
    }
    let body_len = seq.len() - 4;
    if body_len % 4 != 0 {
        return Err(PhysicalError::InvalidBodyLength(body_len));
    }
    let prefix = &seq[..4];
    let body = &seq[4..];

    let perm_idx = PREFIX_CODES
        .iter()
        .position(|&p| p == prefix)
        .ok_or_else(|| PhysicalError::UnknownPrefix(prefix.to_string()))?;
    let perm = &BASE_PERMUTATIONS[perm_idx];

    let chars: Vec<char> = body.chars().collect();
    let mut out = Vec::with_capacity(body_len / 4);
    for chunk in chars.chunks(4) {
        out.push(bases_to_byte(chunk, perm)?);
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn round_trip_simple() {
        let data = b"Hello AeonScript world.";
        let seq = bytes_to_dna(data).unwrap();
        assert!(seq.chars().all(|c| "ACGT".contains(c)));
        let decoded = dna_to_bytes(&seq).unwrap();
        assert_eq!(decoded.as_slice(), data);
    }

    #[test]
    fn empty_input() {
        let seq = bytes_to_dna(b"").unwrap();
        assert_eq!(seq.len(), 4); // just the prefix
        let decoded = dna_to_bytes(&seq).unwrap();
        assert_eq!(decoded.as_slice(), b"");
    }

    #[test]
    fn rejects_short_input_in_decode() {
        let result = dna_to_bytes("ACG");
        assert!(matches!(result, Err(PhysicalError::SequenceTooShort)));
    }

    #[test]
    fn rejects_unknown_prefix() {
        let result = dna_to_bytes("NNNNACGT");
        assert!(matches!(result, Err(PhysicalError::UnknownPrefix(_))));
    }
}
