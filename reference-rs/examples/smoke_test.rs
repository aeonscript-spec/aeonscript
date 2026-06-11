//! End-to-end smoke test for the Rust reference.
//!
//! Run with: `cargo run --example smoke_test`

use aeonscript::{decode_oligos, encode_bytes};

fn main() {
    let passage = "« La mémoire de l'humanité ne devrait pas être propriétaire. »\n\nTest smoke L1+L5 du codec AeonScript en Rust.".as_bytes();

    println!("======================================================================");
    println!("  AeonScript Rust smoke test");
    println!("======================================================================");
    println!("Original payload: {} bytes", passage.len());

    let oligos = encode_bytes(passage, "text/plain", "smoke-rs-1").expect("encode failed");
    let total_bases: usize = oligos.iter().map(|o| o.len()).sum();
    println!(
        "Encoded into {} oligos, total {} bases ({:.3} bits/base, L4 passthrough)",
        oligos.len(),
        total_bases,
        (passage.len() as f64) * 8.0 / total_bases as f64
    );

    println!("\n--- First 3 oligos ---");
    for (i, o) in oligos.iter().take(3).enumerate() {
        let preview: String = o.chars().take(60).collect();
        let trailing = if o.len() > 60 { "..." } else { "" };
        println!("  [{}] ({}b) {}{}", i, o.len(), preview, trailing);
    }

    let recovered = decode_oligos(&oligos).expect("decode failed");
    if recovered.as_slice() == passage {
        println!("\n✓ Round-trip OK — bytes identical");
    } else {
        eprintln!("\n✗ MISMATCH — encoder/decoder bug");
        std::process::exit(1);
    }
}
