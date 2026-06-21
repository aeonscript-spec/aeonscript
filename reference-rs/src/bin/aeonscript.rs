//! `aeonscript` — command-line interface for the AeonScript reference codec.
//!
//! ```text
//! aeonscript encode <input> [-o <out.fasta>] [--mime <type>] [--id <id>] [--len <bases>]
//! aeonscript decode <input.fasta> [-o <out.bin>]
//! aeonscript --help
//! ```
//!
//! `encode` reads an arbitrary file and writes a FASTA pool of synthesizable
//! DNA oligos. `decode` reads such a FASTA pool and reconstructs the original
//! bytes. A round-trip is byte-for-byte exact:
//!
//! ```text
//! aeonscript encode photo.jpg -o pool.fasta
//! aeonscript decode pool.fasta -o photo.out.jpg   # photo.out.jpg == photo.jpg
//! ```

use aeonscript::encoder::{encode_bytes_full, DEFAULT_OLIGO_LENGTH};
use aeonscript::{decode_oligos, CRATE_VERSION, SPEC_VERSION};
use std::io::Write;
use std::process::ExitCode;

const USAGE: &str = "\
aeonscript — open standard for DNA-based information archival

USAGE:
    aeonscript encode <input> [OPTIONS]
    aeonscript decode <input.fasta> [OPTIONS]
    aeonscript --help | --version

ENCODE OPTIONS:
    -o, --out <file>     Output FASTA file (default: stdout)
        --mime <type>    MIME type recorded in the L5 tag (default: application/octet-stream)
        --id <id>        Block identifier recorded in the L5 tag (default: input file name)
        --len <bases>    Target oligo length in bases (default: 200, minimum 64)

DECODE OPTIONS:
    -o, --out <file>     Output file for recovered bytes (default: stdout)

EXAMPLES:
    aeonscript encode manifesto.txt -o pool.fasta --mime text/plain --id manifesto
    aeonscript decode pool.fasta -o recovered.txt
";

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    match run(&args) {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("aeonscript: error: {e}");
            ExitCode::FAILURE
        }
    }
}

fn run(args: &[String]) -> Result<(), String> {
    let cmd = args.first().map(String::as_str);
    match cmd {
        Some("--help") | Some("-h") | None => {
            print!("{USAGE}");
            Ok(())
        }
        Some("--version") | Some("-V") => {
            println!("aeonscript {CRATE_VERSION} (spec v{SPEC_VERSION})");
            Ok(())
        }
        Some("encode") => cmd_encode(&args[1..]),
        Some("decode") => cmd_decode(&args[1..]),
        Some(other) => Err(format!(
            "unknown command '{other}'. Run `aeonscript --help`."
        )),
    }
}

/// Minimal flag parser: pulls `--flag value` / `-f value` pairs out of the
/// argument list, leaving positional arguments behind.
struct Flags {
    positional: Vec<String>,
    out: Option<String>,
    mime: Option<String>,
    id: Option<String>,
    len: Option<usize>,
}

fn parse_flags(args: &[String]) -> Result<Flags, String> {
    let mut f = Flags {
        positional: Vec::new(),
        out: None,
        mime: None,
        id: None,
        len: None,
    };
    let mut i = 0;
    while i < args.len() {
        let a = args[i].clone();
        match a.as_str() {
            "-o" | "--out" => f.out = Some(next_value(args, &mut i, "--out")?),
            "--mime" => f.mime = Some(next_value(args, &mut i, "--mime")?),
            "--id" => f.id = Some(next_value(args, &mut i, "--id")?),
            "--len" => {
                let v = next_value(args, &mut i, "--len")?;
                f.len = Some(
                    v.parse::<usize>()
                        .map_err(|_| format!("--len expects a number, got '{v}'"))?,
                );
            }
            s if s.starts_with('-') => return Err(format!("unknown flag '{s}'")),
            _ => f.positional.push(a),
        }
        i += 1;
    }
    Ok(f)
}

/// Consume the value following a flag, advancing the cursor past it.
fn next_value(args: &[String], i: &mut usize, name: &str) -> Result<String, String> {
    *i += 1;
    args.get(*i)
        .cloned()
        .ok_or_else(|| format!("flag '{name}' expects a value"))
}

fn cmd_encode(args: &[String]) -> Result<(), String> {
    let f = parse_flags(args)?;
    let input = f
        .positional
        .first()
        .ok_or("encode needs an input file. Run `aeonscript --help`.")?;

    let data = std::fs::read(input).map_err(|e| format!("cannot read '{input}': {e}"))?;
    let mime = f.mime.as_deref().unwrap_or("application/octet-stream");
    let id = f.id.clone().unwrap_or_else(|| file_stem(input));
    let len = f.len.unwrap_or(DEFAULT_OLIGO_LENGTH);

    let oligos =
        encode_bytes_full(&data, mime, &id, len).map_err(|e| format!("encoding failed: {e}"))?;

    let total_bases: usize = oligos.iter().map(String::len).sum();
    let mut fasta = String::new();
    for (i, oligo) in oligos.iter().enumerate() {
        fasta.push_str(&format!(">{id}|{i}\n{oligo}\n"));
    }

    write_out(f.out.as_deref(), fasta.as_bytes())?;
    eprintln!(
        "encoded {} bytes -> {} oligos ({} bases) [mime={mime} id={id}]",
        data.len(),
        oligos.len(),
        total_bases
    );
    Ok(())
}

fn cmd_decode(args: &[String]) -> Result<(), String> {
    let f = parse_flags(args)?;
    let input = f
        .positional
        .first()
        .ok_or("decode needs an input FASTA file. Run `aeonscript --help`.")?;

    let text = std::fs::read_to_string(input).map_err(|e| format!("cannot read '{input}': {e}"))?;
    let oligos = parse_fasta(&text);
    if oligos.is_empty() {
        return Err(format!("no oligos found in '{input}'"));
    }

    let bytes = decode_oligos(&oligos).map_err(|e| format!("decoding failed: {e}"))?;
    write_out(f.out.as_deref(), &bytes)?;
    eprintln!("decoded {} oligos -> {} bytes", oligos.len(), bytes.len());
    Ok(())
}

/// Parse a FASTA string into ordered oligo sequences. Sequence lines belonging
/// to the same record are concatenated; whitespace is stripped.
fn parse_fasta(text: &str) -> Vec<String> {
    let mut oligos = Vec::new();
    let mut current = String::new();
    let mut in_record = false;
    for line in text.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        if line.starts_with('>') {
            if in_record {
                oligos.push(std::mem::take(&mut current));
            }
            in_record = true;
        } else {
            current.push_str(line);
        }
    }
    if in_record && !current.is_empty() {
        oligos.push(current);
    }
    oligos
}

/// Derive a default block id from an input path: the file stem, sanitized to
/// the characters AeonScript tags allow (alphanumeric, `-`, `_`, `.`).
fn file_stem(path: &str) -> String {
    let name = path
        .rsplit(['/', '\\'])
        .next()
        .unwrap_or(path);
    let stem = name.split('.').next().unwrap_or(name);
    let cleaned: String = stem
        .chars()
        .map(|c| if c.is_ascii_alphanumeric() || c == '-' || c == '_' { c } else { '_' })
        .collect();
    if cleaned.is_empty() {
        "block".to_string()
    } else {
        cleaned
    }
}

/// Write `bytes` to a file, or to stdout when `out` is `None`.
fn write_out(out: Option<&str>, bytes: &[u8]) -> Result<(), String> {
    match out {
        Some(path) => {
            std::fs::write(path, bytes).map_err(|e| format!("cannot write '{path}': {e}"))
        }
        None => {
            std::io::stdout()
                .write_all(bytes)
                .map_err(|e| format!("cannot write to stdout: {e}"))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use aeonscript::encoder::encode_bytes;

    #[test]
    fn fasta_round_trip_through_library() {
        // encode → render FASTA (as the CLI does) → parse FASTA → decode
        let data = b"AeonScript CLI round-trip \x00\x01\x02 binary-safe.";
        let oligos = encode_bytes(data, "application/octet-stream", "cli_test").unwrap();

        let mut fasta = String::new();
        for (i, o) in oligos.iter().enumerate() {
            fasta.push_str(&format!(">cli_test|{i}\n{o}\n"));
        }

        let parsed = parse_fasta(&fasta);
        assert_eq!(parsed, oligos, "FASTA parse must recover the exact oligos");

        let decoded = decode_oligos(&parsed).unwrap();
        assert_eq!(decoded.as_slice(), data, "round-trip must be byte-exact");
    }

    #[test]
    fn parse_fasta_handles_multiline_and_blank_lines() {
        let fasta = ">a|0\nACGT\nACGT\n\n>a|1\nTTTT\n";
        let parsed = parse_fasta(fasta);
        assert_eq!(parsed, vec!["ACGTACGT".to_string(), "TTTT".to_string()]);
    }

    #[test]
    fn file_stem_sanitizes_paths() {
        assert_eq!(file_stem("photo.jpg"), "photo");
        assert_eq!(file_stem("/tmp/My Doc.v2.txt"), "My_Doc");
        assert_eq!(file_stem(r"C:\dir\report-final.pdf"), "report-final");
        assert_eq!(file_stem("...."), "block");
    }

    #[test]
    fn flags_parse_out_and_len() {
        let args: Vec<String> = ["input.bin", "-o", "out.fasta", "--len", "120"]
            .iter()
            .map(|s| s.to_string())
            .collect();
        let f = parse_flags(&args).unwrap();
        assert_eq!(f.positional, vec!["input.bin".to_string()]);
        assert_eq!(f.out.as_deref(), Some("out.fasta"));
        assert_eq!(f.len, Some(120));
    }
}
