//! High-level AeonScript decoder.
//!
//! Inverse of [`crate::encoder`]:
//!
//! 1. L1 — concatenate decoded bytes from each oligo.
//! 2. Descrambler — XOR with the same PRBS stream (self-inverse).
//! 3. L4 — Reed-Solomon decode (skeleton in v0.1, passes through).
//! 4. L5 — parse and strip the semantic tag.
//! 5. Trim the payload to the declared length.

use crate::error_correction::{decode_with_ecc, EccError, DEFAULT_BLOCK, DEFAULT_NSYM};
use crate::physical::{dna_to_bytes, PhysicalError};
use crate::scrambler::descramble;
use crate::semantic::{parse_tag, validate_tag, TagError};

/// Errors produced by the decoder.
#[derive(Debug, thiserror::Error)]
#[allow(missing_docs)]
pub enum DecodeError {
    #[error("L1 decode failed: {0}")]
    Physical(#[from] PhysicalError),
    #[error("L4 decode failed: {0}")]
    Ecc(#[from] EccError),
    #[error("L5 tag error: {0}")]
    Tag(#[from] TagError),
    #[error("Decoded stream does not start with a tag '|'")]
    MissingTagStart,
    #[error("Decoded stream is missing the closing '|' of the tag")]
    MissingTagEnd,
    #[error("Tag is not valid ASCII")]
    NonAsciiTag,
}

/// Decode a list of AeonScript DNA oligos back to the original payload bytes.
pub fn decode_oligos(oligos: &[String]) -> Result<Vec<u8>, DecodeError> {
    // L1: oligos → bytes
    let mut rs_encoded = Vec::new();
    for o in oligos {
        rs_encoded.extend(dna_to_bytes(o)?);
    }

    // Descrambler
    let plain = descramble(&rs_encoded);

    // L4: Reed-Solomon if the byte stream looks RS-encoded (length is a
    // positive multiple of the full block size 255). Otherwise we assume
    // L4=none (plaintext) — which is what the canonical L1+L5 test vectors
    // use.
    let full_block = DEFAULT_BLOCK + DEFAULT_NSYM;
    let after_l4 = if plain.len() >= full_block && plain.len() % full_block == 0 {
        match decode_with_ecc(&plain, DEFAULT_NSYM, DEFAULT_BLOCK) {
            Ok((decoded, _)) => decoded,
            // RS decode failure on aligned input is genuine corruption.
            Err(e) => return Err(DecodeError::Ecc(e)),
        }
    } else {
        plain
    };

    // L5: find the tag
    if after_l4.first() != Some(&b'|') {
        return Err(DecodeError::MissingTagStart);
    }
    let end_idx = after_l4
        .iter()
        .skip(1)
        .position(|&b| b == b'|')
        .map(|p| p + 1)
        .ok_or(DecodeError::MissingTagEnd)?;

    let tag_bytes = &after_l4[..=end_idx];
    let tag_str = std::str::from_utf8(tag_bytes).map_err(|_| DecodeError::NonAsciiTag)?;
    let tag = parse_tag(tag_str)?;
    validate_tag(&tag)?;

    let len = tag.payload_len().unwrap_or(0);
    let payload_start = end_idx + 1;
    let payload_end = (payload_start + len).min(after_l4.len());
    Ok(after_l4[payload_start..payload_end].to_vec())
}
