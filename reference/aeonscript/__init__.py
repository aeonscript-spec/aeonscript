"""AeonScript — Reference Python implementation.

A minimal-dependency reference codec for the AeonScript specification v0.1.
Supports L1 (physical), L4 (Reed-Solomon error correction), and L5 (semantic tags).

Public API:
    encode_file(path, ...)  -> List[str]  oligos
    encode_bytes(data, ...) -> List[str]  oligos
    decode_oligos(oligos)   -> bytes      original payload
"""

from .encoder import encode_file, encode_bytes
from .decoder import decode_oligos
from .physical import bits_to_dna, dna_to_bits
from .semantic import make_tag, parse_tag

__version__ = "0.1.0"
__spec_version__ = "0.1"

__all__ = [
    "encode_file",
    "encode_bytes",
    "decode_oligos",
    "bits_to_dna",
    "dna_to_bits",
    "make_tag",
    "parse_tag",
    "__version__",
    "__spec_version__",
]
