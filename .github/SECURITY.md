# Security Policy

## Supported Versions

AeonScript is currently in early development (v0.1). Only the latest release is supported for security fixes.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

If you believe you have found a vulnerability in the AeonScript reference codec or specification, **please do not open a public GitHub issue**. Instead, contact us privately so we can investigate and address the issue before disclosure.

### How to report

- **Email**: `security@aeonscript.org` *(mailbox setup in progress — until DNS active, use `mmdrame2017+aeonscript-security@gmail.com`)*
- **GitHub Private Vulnerability Reporting**: https://github.com/aeonscript-spec/aeonscript/security/advisories/new

Please include in your report:
- A description of the vulnerability and its impact
- Steps to reproduce or proof-of-concept code
- The version of the spec or reference codec affected
- Any suggested mitigation, if you have one

### What to expect

- We will acknowledge receipt within **72 hours**
- We will provide an initial assessment within **7 days**
- We will work with you on a fix and coordinated disclosure timeline
- We will credit you in the security advisory unless you prefer to remain anonymous

## Scope

In scope:
- Vulnerabilities in the reference codec (`reference/aeonscript/`) — e.g. buffer over-reads, denial-of-service on malformed input, incorrect error handling that could lead to silent corruption
- Cryptographic weaknesses in the L4/L6 design (when implemented)
- Spec ambiguities that could lead to incompatible or unsafe implementations
- **Bio-safety**: any pathway by which a conformant encoder could be made to emit DNA sequences matching pathogen signatures (in violation of SPEC §9)

Out of scope:
- Issues in third-party dependencies (report upstream)
- Issues in unofficial implementations not endorsed by this repository
- Generic Python / Node tooling vulnerabilities unrelated to AeonScript code

## Bio-safety reporting

Because AeonScript explicitly targets DNA synthesis pipelines, the project takes bio-safety seriously. If you discover:

- A way to bypass the hazard-database screening required by SPEC §9
- A pattern of encoding that could inadvertently produce a dangerous DNA sequence
- A flaw in the screening logic itself

…please report it through the same channels above, and we will additionally notify the relevant international gene synthesis screening bodies (IGSC) when appropriate.

## Out-of-scope but always welcome

For non-security issues (bugs, feature requests, spec discussions), please use the public Issue tracker or Discussions.

---

*Last updated: May 2026 — to be refined as the project matures and a formal security team is established (Phase 2 of [ROADMAP.md](../ROADMAP.md)).*
