//! # AeonScript — Rust reference implementation
//!
//! An open standard for archiving information on DNA.
//! See <https://aeonscript.org> for the full specification.
//!
//! This crate is the canonical Rust reference. It is byte-compatible with
//! the Python and Node reference implementations on every test vector.
//!
//! # Quick start
//!
//! ```
//! use aeonscript::{encode_bytes, decode_oligos};
//!
//! let payload = b"hello aeonscript";
//! let oligos = encode_bytes(payload, "text/plain", "demo").unwrap();
//! let recovered = decode_oligos(&oligos).unwrap();
//! assert_eq!(recovered.as_slice(), payload);
//! ```

#![deny(missing_docs)]
#![warn(rust_2018_idioms)]

pub mod biosafety;
pub mod decoder;
pub mod encoder;
pub mod error_correction;
pub mod physical;
pub mod scrambler;
pub mod semantic;

pub use decoder::decode_oligos;
pub use encoder::{encode_bytes, EncodeError};
pub use semantic::{make_tag, parse_tag, Tag};

/// The version of the AeonScript spec this crate implements.
pub const SPEC_VERSION: &str = "0.1";

/// The crate version (semantic versioning).
pub const CRATE_VERSION: &str = env!("CARGO_PKG_VERSION");
