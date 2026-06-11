//! Layer 4 — Reed-Solomon error correction.
//!
//! This module is a thin wrapper over the [`reed_solomon_erasure`] crate.
//! The default geometry is RS(255, 223) over GF(256), matching the Python
//! reference (which uses `reedsolo`).
//!
//! v0.1 reference implementation: skeleton only — full RS encoding will be
//! wired in v0.1.1. For now, the `encode_with_ecc` function passes data
//! through untouched, with the L4 tag value set to `none` by the encoder.
//!
//! This compromise lets us ship a Rust v0.1 skeleton that compiles and
//! round-trips L1+L5, while keeping the RS integration as a clean follow-up
//! PR. The Python reference is the canonical L4 implementation for v0.1.

/// Errors produced by the L4 codec.
#[derive(Debug, thiserror::Error)]
#[allow(missing_docs)]
pub enum EccError {
    #[error("Reed-Solomon decoding failed: {0}")]
    DecodeFailed(String),
    #[error("Invalid block size {0} (must be ≤ 255 with parity)")]
    InvalidBlockSize(usize),
}

/// Default number of parity bytes per RS block. Per SPEC §3.1.
pub const DEFAULT_NSYM: usize = 32;
/// Default data bytes per RS block (n=255 − nsym).
pub const DEFAULT_BLOCK: usize = 223;

/// Encode bytes with Reed-Solomon RS(255, 223).
///
/// **v0.1 skeleton**: passes data through unchanged. The full implementation
/// will use [`reed_solomon_erasure`] in v0.1.1.
pub fn encode_with_ecc(data: &[u8], _nsym: usize, _block_size: usize) -> Vec<u8> {
    // TODO(v0.1.1): real RS encoding via reed-solomon-erasure
    data.to_vec()
}

/// Decode RS-encoded bytes, returning (payload, total_errors_corrected).
///
/// **v0.1 skeleton**: passes data through unchanged.
pub fn decode_with_ecc(
    data: &[u8],
    _nsym: usize,
    _block_size: usize,
) -> Result<(Vec<u8>, usize), EccError> {
    Ok((data.to_vec(), 0))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn passthrough_round_trip_v01_skeleton() {
        let data = b"some payload bytes";
        let encoded = encode_with_ecc(data, DEFAULT_NSYM, DEFAULT_BLOCK);
        let (decoded, n_err) = decode_with_ecc(&encoded, DEFAULT_NSYM, DEFAULT_BLOCK).unwrap();
        assert_eq!(decoded.as_slice(), data);
        assert_eq!(n_err, 0);
    }
}
