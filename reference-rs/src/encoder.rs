//! High-level AeonScript encoder.
//!
//! Pipeline (top-to-bottom):
//!
//! 1. L5 — prepend the semantic tag.
//! 2. L4 — apply Reed-Solomon error correction (skeleton in v0.1, passes through).
//! 3. Scrambler — xorshift32 PRBS to balance GC content.
//! 4. L1 — encode bytes as DNA with constraint-aware base permutations.
//! 5. Chunk into oligos of the configured target length.

use crate::error_correction::{encode_with_ecc, EccError, DEFAULT_BLOCK, DEFAULT_NSYM};
use crate::physical::{bytes_to_dna, PhysicalError};
use crate::scrambler::scramble;
use crate::semantic::{make_tag, validate_tag_value, TagError};

/// Default target oligo length in bases, per SPEC §2.4.
pub const DEFAULT_OLIGO_LENGTH: usize = 200;

/// Errors produced by the encoder.
#[derive(Debug, thiserror::Error)]
#[allow(missing_docs)]
pub enum EncodeError {
    #[error("L1 encoding failed: {0}")]
    Physical(#[from] PhysicalError),
    #[error("L4 RS encoding failed: {0}")]
    Ecc(#[from] EccError),
    #[error("L5 tag error: {0}")]
    Tag(#[from] TagError),
    #[error("Oligo length too small (minimum is 64 bases, got {0})")]
    OligoTooSmall(usize),
}

/// Encode arbitrary bytes into a list of DNA oligos.
///
/// Each returned [`String`] is a synthesizable DNA sequence (only `A`,
/// `C`, `G`, `T`), of approximately `DEFAULT_OLIGO_LENGTH` bases.
pub fn encode_bytes(
    data: &[u8],
    mime_type: &str,
    block_id: &str,
) -> Result<Vec<String>, EncodeError> {
    encode_bytes_full(data, mime_type, block_id, DEFAULT_OLIGO_LENGTH)
}

/// Encode bytes with an explicit oligo target length.
pub fn encode_bytes_full(
    data: &[u8],
    mime_type: &str,
    block_id: &str,
    oligo_length: usize,
) -> Result<Vec<String>, EncodeError> {
    if oligo_length < 64 {
        return Err(EncodeError::OligoTooSmall(oligo_length));
    }

    // L5: validate then build the semantic tag
    validate_tag_value("mime_type", mime_type)?;
    validate_tag_value("block_id", block_id)?;
    let tag = make_tag(mime_type, data.len(), block_id);

    let mut tagged = tag.into_bytes();
    tagged.extend_from_slice(data);

    // L4: Reed-Solomon RS(255, 223) over GF(256)
    let rs_encoded = encode_with_ecc(&tagged, DEFAULT_NSYM, DEFAULT_BLOCK)?;

    // Scrambler: uniformise byte distribution
    let stream = scramble(&rs_encoded);

    // L1: chunk into oligos
    let bytes_per_oligo = (oligo_length - 4) / 4;
    let mut oligos = Vec::new();
    for chunk in stream.chunks(bytes_per_oligo) {
        oligos.push(bytes_to_dna(chunk)?);
    }
    Ok(oligos)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::decoder::decode_oligos;

    #[test]
    fn round_trip_short_text() {
        let data = b"AeonScript round-trip test.";
        let oligos = encode_bytes(data, "text/plain", "t1").unwrap();
        let decoded = decode_oligos(&oligos).unwrap();
        assert_eq!(decoded.as_slice(), data);
    }

    #[test]
    fn rejects_mime_with_semicolon() {
        let result = encode_bytes(b"x", "text/plain; charset=utf-8", "t1");
        assert!(matches!(result, Err(EncodeError::Tag(TagError::ReservedCharacters { .. }))));
    }
}
