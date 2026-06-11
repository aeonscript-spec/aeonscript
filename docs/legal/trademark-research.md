# Trademark research — "AeonScript"

**Date** : 2026-06-07
**Researcher** : informal (not legal counsel)
**Status** : preliminary — formal IP review required before any registration

---

## Summary

| Finding | Status |
|---|---|
| Exact "AeonScript" trademark registered in USPTO | ❌ Not found |
| Exact "AeonScript" trademark registered in EUIPO | ❌ Not found |
| Exact "AeonScript" trademark registered in INPI (France) | ❌ Not found (preliminary) |
| Exact "AeonScript" GitHub organisation | ✓ Owned by us (aeonscript-spec) |
| Exact "AeonScript" PyPI package | ❌ Not found |
| Exact "AeonScript" npm package | ❌ Not found |
| Domain `aeonscript.org` | ✓ Owned by us |
| Domain `aeonscript.io` | ✓ Owned by us |
| Domain `aeonscript.com` | ❌ Taken (status unknown — squatter or active?) |
| Domain `aeonscript.net` | ❌ Taken (status unknown) |

**Preliminary conclusion** : the name "AeonScript" appears available for trademark registration in software/standards classes (Nice class 9, software; class 42, technical services). No active competing use in the DNA storage, bioinformatics, or information-theory domain was found.

---

## Adjacent / similar names (low conflict risk but noted)

| Name | Source | Conflict probability |
|---|---|---|
| **aeon-script** (kanarb) | GitHub repo — script for UCSC library Aeon system | Very low — different domain (library science), no trademark, GitHub-only |
| **aeon** (aaronjmars) | GitHub repo — autonomous agent framework | Low — different category, "Aeon" alone is generic |
| **AionScript** | Multiple GitHub repos | Low — pertains to the Aion video game, different industry |
| **Aeon Products, Inc.** | USPTO registration | None — "AEON" word mark in physical goods, unrelated class |
| **Aeon Co., Ltd.** (Japan) | EUIPO/JPO — major Japanese retailer | None — different class entirely |
| **Aeon Solar** | Various | None — different industry |

The word *"Aeon"* alone is too generic to monopolise. *"AeonScript"* as a compound name appears unclaimed in the software-standards space.

---

## Risks and mitigation

### Risk 1 — A future "AeonScript" trademark filing by someone else

**Probability** : medium if the project gains traction without registering.
**Impact** : forced rename (with the cost of losing accumulated visibility, SEO, social handles).
**Mitigation** : file a defensive trademark in **classes 9 (software) and 42 (technical services)** at:

- **USPTO** (US) — ~$350–$1,750 per class via standard or TEAS Plus. Estimated cost: **$700–$2,000 for both classes**, plus ~$1,000 if using a lawyer.
- **EUIPO** (EU) — ~€850 for the first class, ~€50 for second class. Estimated: **~€900**.
- **INPI** (France, optional if EUIPO is filed) — ~€190 for one class, ~€40 per additional. Estimated: **~€230**.

**Recommended sequence** (in order of priority):

1. **EUIPO first** — covers 27 countries including France and Germany, where institutional adoption (BnF, EBI, DNB) is most plausible.
2. **USPTO** second — covers the US market and Microsoft / Twist / Catalog HQ jurisdictions.
3. **Madrid Protocol extension** later — covers Japan, China, Brazil, etc.

### Risk 2 — A passive trademark "stash" registration

Sometimes squatters register names speculatively and demand licensing fees. The fact that `aeonscript.com` and `aeonscript.net` are already taken suggests there may be some interest already.

**Mitigation** : check the WHOIS of `.com` and `.net`. If they're parked by squatters with no trademark, we can ignore. If they're owned by an entity with a registered "AeonScript" mark in a relevant class, we have a problem.

### Risk 3 — Trademark on similar name in our class

`aeon-script` (kanarb) is the closest match. It's an open-source GitHub repo, hasn't been touched in years, and is not associated with a registered trademark. **Negligible risk** unless we attempt to claim "Aeon Script" with a space — we should always brand as *AeonScript* (one word, no space) to maintain distinctiveness.

---

## Recommendations

### Immediate (before launch)

- [x] Document this research in the repo (this file).
- [ ] WHOIS check `aeonscript.com` and `aeonscript.net` to identify owners — *to be done before launch*.

### Short term (within 30 days of launch)

- [ ] Engage an IP lawyer for a formal clearance search (~€500–€1,500).
- [ ] File EUIPO trademark in classes 9 + 42 (~€900).
- [ ] Document the trademark policy in `TRADEMARK.md` (à la Apache, Mozilla).

### Long term (within 12 months)

- [ ] File USPTO trademark in classes 9 + 42 (~$700–$2,000).
- [ ] Consider Madrid Protocol extension to JP, CA, AU.

---

## A trademark policy for "AeonScript"

Once the trademark is held by the future AeonScript Foundation (or, in the interim, by the project's maintainers as legal placeholder), the policy should allow:

- ✓ Citing "AeonScript" in academic publications, blog posts, news articles
- ✓ Calling an implementation "AeonScript-compatible" provided it passes the conformance suite
- ✓ Forking the codebase and distributing under any name *other than* "AeonScript"
- ✗ Using "AeonScript" as the name of a non-conformant implementation
- ✗ Using "AeonScript" as a company name or product line without authorisation
- ✗ Registering domains containing "AeonScript" without permission

This is the standard Mozilla / Apache pattern, adapted.

---

## Disclaimer

This research is **not legal advice**. The author is not a trademark lawyer. The conclusions above are based on publicly accessible search engines and registry websites at the time of writing. A formal clearance search by a qualified IP professional is required before any actual trademark filing.

If you spot an error or omission in this research, please [open an issue](https://github.com/aeonscript-spec/aeonscript/issues).

---

## Sources

- [USPTO Trademark Search](https://tmsearch.uspto.gov/)
- [EUIPO Trade Mark Search](https://www.euipo.europa.eu/en/trade-marks/before-applying/availability)
- [INPI base marques](https://data.inpi.fr/)
- [GitHub kanarb/aeon-script](https://github.com/kanarb/aeon-script)
- [GitHub aaronjmars/aeon](https://github.com/aaronjmars/aeon)
- [FOSSmarks — open source trademark guide](https://fossmarks.org/)
- [Apache Software Foundation Trademark Policy](https://www.apache.org/foundation/marks/)
