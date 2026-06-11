//! Layer 4 — Reed-Solomon error correction over GF(256).
//!
//! Thin wrapper over the [`reed_solomon`] crate. The default geometry is
//! RS(255, 223) matching the Python reference (which uses `reedsolo`).
//! Conformant implementations MUST produce byte-identical codewords given
//! identical inputs.

use reed_solomon::{Decoder, Encoder};

/// Errors produced by the L4 codec.
#[derive(Debug, thiserror::Error)]
#[allow(missing_docs)]
pub enum EccError {
    #[error("Reed-Solomon decoding failed (too many errors): {0}")]
    DecodeFailed(String),
    #[error("Invalid block size {0} (must be <= 255 with parity)")]
    InvalidBlockSize(usize),
    #[error("Encoded data length {0} not a multiple of full block size {1}")]
    UnalignedData(usize, usize),
}

/// Default number of parity bytes per RS block. Per SPEC §3.1.
pub const DEFAULT_NSYM: usize = 32;
/// Default data bytes per RS block (n = 255 − nsym).
pub const DEFAULT_BLOCK: usize = 223;

/// Encode a single RS block: `data.len() + nsym` bytes (data followed by parity).
pub fn rs_encode_msg(data: &[u8], nsym: usize) -> Result<Vec<u8>, EccError> {
    if data.len() + nsym > 255 {
        return Err(EccError::InvalidBlockSize(data.len() + nsym));
    }
    let encoder = Encoder::new(nsym);
    let encoded = encoder.encode(data);
    Ok(encoded.iter().copied().collect())
}

/// Decode a single RS codeword. Returns (decoded_message_bytes, errors_corrected).
pub fn rs_decode_msg(codeword: &[u8], nsym: usize) -> Result<(Vec<u8>, usize), EccError> {
    let decoder = Decoder::new(nsym);
    let result = decoder
        .correct(codeword, None)
        .map_err(|e| EccError::DecodeFailed(format!("{:?}", e)))?;
    let n_errs = result.errors_count();
    let msg: Vec<u8> = result.data().to_vec();
    Ok((msg, n_errs))
}

/// Split `data` into RS blocks of size `block_size` (zero-padding the last)
/// and encode each. Output length = N × (block_size + nsym).
pub fn encode_with_ecc(data: &[u8], nsym: usize, block_size: usize) -> Result<Vec<u8>, EccError> {
    let mut out = Vec::new();
    for chunk in data.chunks(block_size) {
        let mut padded = chunk.to_vec();
        if padded.len() < block_size {
            padded.resize(block_size, 0);
        }
        out.extend(rs_encode_msg(&padded, nsym)?);
    }
    Ok(out)
}

/// Decode RS-encoded data, returning (concatenated_payload_bytes, total_errors_corrected).
/// Caller (decoder.rs) trims the payload based on the L5 LEN field.
pub fn decode_with_ecc(
    data: &[u8],
    nsym: usize,
    block_size: usize,
) -> Result<(Vec<u8>, usize), EccError> {
    let full_block = block_size + nsym;
    if data.len() % full_block != 0 {
        return Err(EccError::UnalignedData(data.len(), full_block));
    }
    let mut out = Vec::with_capacity(data.len() - (data.len() / full_block) * nsym);
    let mut total_errors = 0usize;
    for chunk in data.chunks(full_block) {
        let (msg, n_errs) = rs_decode_msg(chunk, nsym)?;
        out.extend(msg);
        total_errors += n_errs;
    }
    Ok((out, total_errors))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn round_trip_no_errors() {
        let data: Vec<u8> = (0..223).collect();
        let encoded = encode_with_ecc(&data, DEFAULT_NSYM, DEFAULT_BLOCK).unwrap();
        assert_eq!(encoded.len(), 255);
        let (decoded, n_errs) = decode_with_ecc(&encoded, DEFAULT_NSYM, DEFAULT_BLOCK).unwrap();
        assert_eq!(decoded, data);
        assert_eq!(n_errs, 0);
    }

    #[test]
    fn corrects_up_to_16_byte_errors() {
        let data: Vec<u8> = (0..223).collect();
        let mut encoded = encode_with_ecc(&data, DEFAULT_NSYM, DEFAULT_BLOCK).unwrap();

        // Flip 10 bytes (well within RS(255,223) 16-error capacity)
        let positions = [3usize, 17, 42, 88, 100, 130, 175, 200, 220, 250];
        for &p in &positions {
            encoded[p] ^= 0xAA;
        }
        let (decoded, n_errs) = decode_with_ecc(&encoded, DEFAULT_NSYM, DEFAULT_BLOCK).unwrap();
        assert_eq!(decoded, data);
        assert_eq!(n_errs, 10);
    }

    #[test]
    fn fails_on_too_many_errors() {
        let data: Vec<u8> = (0..223).collect();
        let mut encoded = encode_with_ecc(&data, DEFAULT_NSYM, DEFAULT_BLOCK).unwrap();
        // Flip 20 bytes (exceeds 16-error capacity)
        for p in 0..20 {
            encoded[p * 10] ^= 0xFF;
        }
        let result = decode_with_ecc(&encoded, DEFAULT_NSYM, DEFAULT_BLOCK);
        assert!(matches!(result, Err(EccError::DecodeFailed(_))));
    }
}
