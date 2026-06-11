//! SPEC §9 — Bio-safety screening (skeleton).
//!
//! A conformant AeonScript encoder MUST screen output oligos against a
//! hazard database before they are emitted for synthesis. This module
//! provides a v0.1 skeleton API.
//!
//! For the canonical hazard signature list, see
//! [`reference/aeonscript/biosafety_hazards.json`](../../reference/aeonscript/biosafety_hazards.json)
//! at the repository root.

/// One match against a hazard signature.
#[derive(Debug, Clone)]
pub struct HazardMatch {
    /// Index of the offending oligo in the input.
    pub oligo_index: usize,
    /// Position within the oligo where the match starts.
    pub position: usize,
    /// Identifier of the hazard signature that matched.
    pub signature_id: String,
    /// Human-readable description of the signature.
    pub signature_description: String,
}

/// Returned when an encoder is asked to emit oligos that match hazard sigs.
#[derive(Debug, thiserror::Error)]
#[error("Bio-safety screening failed: {} hazard match(es)", matches.len())]
pub struct BioSafetyViolation {
    /// All matches found.
    pub matches: Vec<HazardMatch>,
}

/// Screen the given oligos against the hazard database.
///
/// **v0.1 skeleton**: returns an empty list. The full implementation will
/// load the hazard JSON from the shipped resource directory and do
/// forward + reverse-complement substring matching.
pub fn screen_oligos(_oligos: &[String]) -> Vec<HazardMatch> {
    // TODO(v0.1.1): port the Python implementation, embed the hazard JSON
    // via include_str! to keep the Rust crate self-contained.
    Vec::new()
}

/// Enforce SPEC §9 by raising on any hazard match.
pub fn enforce_biosafety(oligos: &[String]) -> Result<(), BioSafetyViolation> {
    let matches = screen_oligos(oligos);
    if matches.is_empty() {
        Ok(())
    } else {
        Err(BioSafetyViolation { matches })
    }
}
