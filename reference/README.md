# aeonscript (reference codec)

Python reference implementation of the AeonScript open standard for DNA-based information archival.

This is the **reference codec** — the canonical implementation against which all other implementations must validate. It is intentionally simple and audit-friendly, not optimised for performance.

## Install

```bash
pip install -e .
# with test deps:
pip install -e ".[test]"
```

## Use

```python
from aeonscript import encode_bytes, decode_oligos

oligos = encode_bytes(b"some payload", mime_type="text/plain", block_id="my-file")
print(f"Encoded into {len(oligos)} oligos")

decoded = decode_oligos(oligos)
assert decoded == b"some payload"
```

## Run tests

```bash
pytest tests/ -v
python examples/encode_demo.py
```

## Architecture

- `aeonscript.physical`  — L1 — binary ↔ DNA encoding with biochemical constraints
- `aeonscript.scrambler` — xorshift32 PRBS to uniformize byte distribution
- `aeonscript.error_correction` — L4 — Reed-Solomon RS(255,223) via `reedsolo`
- `aeonscript.semantic` — L5 — self-describing semantic tags
- `aeonscript.encoder` / `aeonscript.decoder` — top-level API

See the [full spec](https://github.com/aeonscript-spec/aeonscript/blob/main/spec/SPEC-v0.1.md) and the [project landing page](https://aeonscript.org).

## License

MIT.
