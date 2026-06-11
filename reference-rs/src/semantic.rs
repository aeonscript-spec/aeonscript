//! Layer 5 — Session: semantic tags.
//!
//! Tags are ASCII strings of the form `|KEY1=VALUE1;KEY2=VALUE2;...|`
//! and carry self-describing metadata about each block.

use std::collections::BTreeMap;

/// Errors produced when parsing or validating an L5 tag.
#[derive(Debug, thiserror::Error)]
#[allow(missing_docs)]
pub enum TagError {
    #[error("Tag must be wrapped in '|...|'")]
    MissingPipes,
    #[error("Empty tag body")]
    EmptyBody,
    #[error("Malformed tag field (no '='): {0:?}")]
    MalformedField(String),
    #[error("Tag missing mandatory keys: {0:?}")]
    MissingMandatory(Vec<String>),
    #[error("Unsupported AEONSCRIPT version: {0:?}")]
    UnsupportedVersion(String),
    #[error("Unsupported L1 profile: {0:?}")]
    UnsupportedL1(String),
    #[error("LEN must be a non-negative integer (got {0:?})")]
    InvalidLength(String),
    #[error("Tag value for {field} contains reserved characters: {chars:?}")]
    ReservedCharacters {
        /// Which field had the problem.
        field: String,
        /// Which reserved characters were found.
        chars: Vec<char>,
    },
}

const FORBIDDEN_TAG_CHARS: &[char] = &[';', '=', '|'];
const MANDATORY_KEYS: &[&str] = &["AEONSCRIPT", "L1", "L4", "TYPE", "LEN", "ID"];

/// A parsed semantic tag, accessible as a key-value map.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Tag {
    /// All key-value pairs, preserved in insertion order.
    pub fields: BTreeMap<String, String>,
}

impl Tag {
    /// Return the AEONSCRIPT version declared in the tag.
    pub fn version(&self) -> Option<&str> {
        self.fields.get("AEONSCRIPT").map(String::as_str)
    }

    /// Return the L1 profile declared in the tag.
    pub fn l1_profile(&self) -> Option<&str> {
        self.fields.get("L1").map(String::as_str)
    }

    /// Return the declared payload length in bytes.
    pub fn payload_len(&self) -> Option<usize> {
        self.fields.get("LEN").and_then(|v| v.parse().ok())
    }
}

/// Validate that a value does not contain any of the L5-reserved
/// characters (`;`, `=`, `|`). Returns `Err` describing the offence.
pub fn validate_tag_value(field: &str, value: &str) -> Result<(), TagError> {
    let bad: Vec<char> = FORBIDDEN_TAG_CHARS
        .iter()
        .copied()
        .filter(|c| value.contains(*c))
        .collect();
    if bad.is_empty() {
        Ok(())
    } else {
        Err(TagError::ReservedCharacters {
            field: field.to_string(),
            chars: bad,
        })
    }
}

/// Build a canonical AeonScript v0.1 tag string.
///
/// Declares `L4=rs255-223` — matching the Python reference, since the Rust
/// reference now also implements RS(255, 223) via the `reed-solomon` crate.
pub fn make_tag(mime_type: &str, payload_len: usize, block_id: &str) -> String {
    format!(
        "|AEONSCRIPT=0.1;L1=L1-4;L4=rs255-223;TYPE={mime};LEN={len};ID={id}|",
        mime = mime_type,
        len = payload_len,
        id = block_id
    )
}

/// Build a tag with additional optional fields appended after the mandatory ones.
pub fn make_tag_with_extras(
    mime_type: &str,
    payload_len: usize,
    block_id: &str,
    extras: &[(&str, &str)],
) -> String {
    let mut s = format!(
        "AEONSCRIPT=0.1;L1=L1-4;L4=rs255-223;TYPE={mime};LEN={len};ID={id}",
        mime = mime_type,
        len = payload_len,
        id = block_id
    );
    for (k, v) in extras {
        s.push_str(&format!(";{}={}", k, v));
    }
    format!("|{}|", s)
}

/// Parse a tag string back into a [`Tag`] struct.
pub fn parse_tag(tag: &str) -> Result<Tag, TagError> {
    if !(tag.starts_with('|') && tag.ends_with('|')) {
        return Err(TagError::MissingPipes);
    }
    let body = &tag[1..tag.len() - 1];
    if body.is_empty() {
        return Err(TagError::EmptyBody);
    }
    let mut fields = BTreeMap::new();
    for pair in body.split(';') {
        let eq = pair.find('=').ok_or_else(|| TagError::MalformedField(pair.to_string()))?;
        let (key, val) = pair.split_at(eq);
        let val = &val[1..]; // skip the '='
        fields.insert(key.to_string(), val.to_string());
    }
    let missing: Vec<String> = MANDATORY_KEYS
        .iter()
        .filter(|k| !fields.contains_key(**k))
        .map(|s| s.to_string())
        .collect();
    if !missing.is_empty() {
        return Err(TagError::MissingMandatory(missing));
    }
    Ok(Tag { fields })
}

/// Validate the contents of a parsed tag against v0.1 requirements.
pub fn validate_tag(tag: &Tag) -> Result<(), TagError> {
    match tag.version() {
        Some("0.1") => {}
        Some(other) => return Err(TagError::UnsupportedVersion(other.to_string())),
        None => return Err(TagError::UnsupportedVersion("<missing>".to_string())),
    }
    match tag.l1_profile() {
        Some("L1-4") | Some("L1-5m") | Some("L1-6") => {}
        Some(other) => return Err(TagError::UnsupportedL1(other.to_string())),
        None => return Err(TagError::UnsupportedL1("<missing>".to_string())),
    }
    if tag.payload_len().is_none() {
        return Err(TagError::InvalidLength(
            tag.fields.get("LEN").cloned().unwrap_or_default(),
        ));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn round_trip_minimal_tag() {
        let s = make_tag("text/plain", 42, "block-1");
        let tag = parse_tag(&s).unwrap();
        assert_eq!(tag.version(), Some("0.1"));
        assert_eq!(tag.l1_profile(), Some("L1-4"));
        assert_eq!(tag.payload_len(), Some(42));
        assert_eq!(tag.fields.get("ID"), Some(&"block-1".to_string()));
    }

    #[test]
    fn rejects_reserved_characters() {
        assert!(validate_tag_value("mime_type", "text/plain; charset=utf-8").is_err());
        assert!(validate_tag_value("mime_type", "image/png").is_ok());
        assert!(validate_tag_value("id", "bad=key").is_err());
        assert!(validate_tag_value("id", "valid-id-123").is_ok());
    }

    #[test]
    fn rejects_unwrapped_tag() {
        assert!(matches!(parse_tag("AEONSCRIPT=0.1"), Err(TagError::MissingPipes)));
    }

    #[test]
    fn rejects_missing_mandatory_keys() {
        let result = parse_tag("|AEONSCRIPT=0.1|");
        assert!(matches!(result, Err(TagError::MissingMandatory(_))));
    }
}
