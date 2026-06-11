//! xorshift32 PRBS scrambler. Byte-identical to the Python and Node refs.

const SCRAMBLER_SEED: u32 = 0xDEAD_BEEF;

fn xorshift32(state: u32) -> u32 {
    let mut s = state;
    s ^= s << 13;
    s ^= s >> 17;
    s ^= s << 5;
    s
}

/// XOR `data` with a deterministic pseudo-random byte stream seeded by
/// the AeonScript v0.1 canonical seed `0xDEADBEEF`.
///
/// The scrambler is self-inverse: `scramble(scramble(x)) == x`.
pub fn scramble(data: &[u8]) -> Vec<u8> {
    let mut state = SCRAMBLER_SEED;
    let mut out = Vec::with_capacity(data.len());
    for &b in data {
        state = xorshift32(state);
        out.push(b ^ ((state & 0xFF) as u8));
    }
    out
}

/// Alias for [`scramble`] — XOR is self-inverse.
pub fn descramble(data: &[u8]) -> Vec<u8> {
    scramble(data)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn self_inverse() {
        let data = b"some arbitrary bytes here";
        let scrambled = scramble(data);
        let descrambled = descramble(&scrambled);
        assert_eq!(descrambled.as_slice(), data);
    }

    #[test]
    fn matches_reference_on_empty() {
        assert!(scramble(b"").is_empty());
    }
}
