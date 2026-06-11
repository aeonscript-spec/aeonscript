//! Conformance test: validate the Rust reference against the canonical
//! L1+L5 test vectors at `spec/test-vectors/vectors-l1-l5.json`.

use aeonscript::decode_oligos;

#[derive(serde::Deserialize)]
struct Vectors {
    vectors: Vec<Vector>,
}

#[derive(serde::Deserialize)]
struct Vector {
    id: String,
    input: VectorInput,
    expected: VectorExpected,
}

#[derive(serde::Deserialize)]
struct VectorInput {
    payload_hex: String,
}

#[derive(serde::Deserialize)]
struct VectorExpected {
    oligos: Vec<String>,
}

fn load_vectors() -> Vectors {
    let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("spec")
        .join("test-vectors")
        .join("vectors-l1-l5.json");
    let text = std::fs::read_to_string(&path)
        .unwrap_or_else(|e| panic!("can't read {}: {}", path.display(), e));
    serde_json::from_str(&text).expect("invalid JSON")
}

fn hex_to_bytes(s: &str) -> Vec<u8> {
    (0..s.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&s[i..i + 2], 16).expect("bad hex"))
        .collect()
}

/// Every canonical vector's oligos must round-trip to the declared payload.
#[test]
fn decoder_conformance_all_vectors() {
    let vecs = load_vectors();
    for v in &vecs.vectors {
        let expected = hex_to_bytes(&v.input.payload_hex);
        // The Rust v0.1 skeleton does NOT include L4 yet, but the canonical
        // vectors at spec/test-vectors/vectors-l1-l5.json use `L4=none`,
        // so they SHOULD round-trip through our skeleton decoder.
        let result = decode_oligos(&v.expected.oligos);
        match result {
            Ok(recovered) => {
                assert_eq!(
                    recovered, expected,
                    "vector {} mismatch: decoder produced wrong bytes",
                    v.id
                );
            }
            Err(e) => {
                panic!("vector {} failed to decode: {:?}", v.id, e);
            }
        }
    }
}
