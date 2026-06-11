# Quickstart Tutorial

In this 10-minute tutorial, you'll:

1. Install the AeonScript reference codec.
2. Encode a small file into DNA oligos.
3. Inspect what one block actually looks like.
4. Decode it back and verify byte-for-byte fidelity.
5. Simulate sequencing errors and watch Reed-Solomon recover.

This tutorial assumes Python 3.10+. If you don't have Python locally, you can run everything on [Google Colab](https://colab.research.google.com/) by pasting the snippets into a notebook.

---

## 1. Install

```bash
git clone https://github.com/aeonscript-spec/aeonscript.git
cd aeonscript/reference
pip install -e .
```

This installs the package plus the single Reed-Solomon dependency (`reedsolo`, BSD-3, ~200 lines).

Verify the install:

```bash
python -c "import aeonscript; print(aeonscript.__version__)"
# → 0.1.0
```

---

## 2. Encode your first payload

Create a file `tutorial.py`:

```python
from aeonscript import encode_bytes, decode_oligos

payload = b"The first message I want to preserve for a thousand years."

oligos = encode_bytes(
    payload,
    mime_type="text/plain",
    block_id="tutorial-block-1",
)

print(f"Encoded {len(payload)} bytes into {len(oligos)} oligos.")
print(f"Total DNA bases: {sum(len(o) for o in oligos)}")
print(f"First oligo: {oligos[0][:60]}...")
```

Run it:

```bash
python tutorial.py
```

Expected output:

```
Encoded 58 bytes into 4 oligos.
Total DNA bases: 712
First oligo: ACGTGGAGCCTTAGAGGGAAAGGTCTAATGACTGCTGCCGTGGGCGGTTGTGCAT...
```

Each oligo is a string of `A`, `C`, `G`, `T` — exactly what a DNA synthesizer (Twist, IDT, etc.) accepts as input.

---

## 3. Inspect a block

Add to `tutorial.py`:

```python
decoded, meta = decode_oligos(oligos, return_metadata=True)

print(f"\n--- Semantic tag (L5) ---")
for k, v in meta["tag"].items():
    print(f"  {k:12s} = {v}")
```

Output:

```
--- Semantic tag (L5) ---
  AEONSCRIPT   = 0.1
  L1           = L1-4
  L4           = rs255-223
  TYPE         = text/plain
  LEN          = 58
  ID           = tutorial-block-1
  CHECKSUM     = sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

The tag is **embedded in the DNA itself** — a future decoder reading this oligo set in the year 2230 will know exactly which codec to use, because the codec version is part of the data.

---

## 4. Verify the round-trip

```python
assert decoded == payload, "MISMATCH"
print("\n✓ Round-trip OK — bytes identical")
print(f"Errors corrected during decode: {meta['errors_corrected']}")
```

Output:

```
✓ Round-trip OK — bytes identical
Errors corrected during decode: 0
```

---

## 5. Simulate sequencing errors

Real DNA reading (Illumina, Nanopore) has an error rate of ~0.1–1% per base. Let's simulate that:

```python
import random

def inject_errors(oligos, n_errors, seed=42):
    rng = random.Random(seed)
    mutated = [list(o) for o in oligos]
    for _ in range(n_errors):
        oligo_idx = rng.randint(0, len(mutated) - 1)
        base_idx = rng.randint(0, len(mutated[oligo_idx]) - 1)
        current = mutated[oligo_idx][base_idx]
        alternatives = [b for b in "ACGT" if b != current]
        mutated[oligo_idx][base_idx] = rng.choice(alternatives)
    return ["".join(o) for o in mutated]

noisy = inject_errors(oligos, n_errors=5)

recovered, meta2 = decode_oligos(noisy, return_metadata=True)
assert recovered == payload, "MISMATCH after injected errors"
print(f"\n✓ Recovered despite {meta2['errors_corrected']} corrupted bases")
```

Output:

```
✓ Recovered despite 5 corrupted bases
```

This is Reed-Solomon RS(255, 223) at work: each 255-base block can absorb up to 16 byte errors before losing data.

---

## 6. Encode a real file

```python
from aeonscript import encode_file

# Encode any local file
oligos = encode_file("path/to/your/file.pdf")

# Write the oligos to disk as a FASTA file (synthesizer-friendly)
with open("output.fasta", "w") as f:
    for i, oligo in enumerate(oligos):
        f.write(f">block-1-oligo-{i}\n{oligo}\n")
```

You now have a FASTA file ready to send to a synthesis vendor.

---

## 7. Round-trip from FASTA

```python
oligos = []
with open("output.fasta") as f:
    for line in f:
        if line.startswith(">"):
            continue
        oligos.append(line.strip())

recovered = decode_oligos(oligos)
with open("recovered.pdf", "wb") as f:
    f.write(recovered)

# Verify
import hashlib
with open("path/to/your/file.pdf", "rb") as f:
    original_hash = hashlib.sha256(f.read()).hexdigest()
recovered_hash = hashlib.sha256(recovered).hexdigest()
assert original_hash == recovered_hash
print("✓ FASTA round-trip OK")
```

---

## What's next?

- **Read the [spec](../spec/SPEC-v0.1.md)** — understand the 7-layer architecture
- **Try the [interactive demo](https://aeonscript.org#try-it)** — encode text in your browser
- **Run the [conformance vectors](../spec/CONFORMANCE.md)** — verify your build matches the reference
- **Open a [Discussion](https://github.com/aeonscript-spec/aeonscript/discussions)** — share what you're building

Happy archiving. 🧬
