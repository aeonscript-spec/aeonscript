# AeonScript

**Un standard ouvert d'archivage de l'information sur ADN.**

[![CI](https://github.com/aeonscript-spec/aeonscript/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/aeonscript-spec/aeonscript/actions/workflows/ci.yml)
[![Spec version](https://img.shields.io/badge/spec-v0.1-blue)](spec/SPEC-v0.1.md)
[![License](https://img.shields.io/badge/license-MIT%20%2B%20CC--BY--SA-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-early%20draft-orange)]()
[![Site](https://img.shields.io/badge/site-aeonscript.org-00d4a8)](https://aeonscript.org)
[![Discussions](https://img.shields.io/github/discussions/aeonscript-spec/aeonscript)](https://github.com/aeonscript-spec/aeonscript/discussions)

---

## Pourquoi

L'ADN permet de stocker **~215 pétaoctets par gramme**, sans énergie, pendant des millénaires. C'est le meilleur support d'archive à long terme jamais découvert. Mais aujourd'hui, chaque acteur industriel (Microsoft, Twist, Catalog…) invente son propre format, propriétaire et incompatible.

**AeonScript est le standard ouvert qui manque.** Pensez TCP/IP pour le stockage ADN.

→ Lire le [Manifeste](MANIFESTO.md).

---

## Quoi

AeonScript est :

- 🧬 **Une spécification ouverte** d'encodage de données numériques sur ADN
- 📐 **Une architecture en 7 couches** (OSI-like : physique, multiplexage, transport, addressage, session, présentation, application)
- 🤖 **Une encodeur AI-natif** exploitant les modèles de fondation génomiques (Evo 2 et successeurs)
- 🏷️ **Un format auto-descriptif** avec tags sémantiques hiérarchiques
- 🛡️ **Un protocole bio-safe** avec filtrage des séquences pathogènes obligatoire
- 📂 **Une implémentation de référence** en Python (Rust prévu)

---

## Démarrage rapide

### Installation

```bash
git clone https://github.com/<TBD>/aeonscript.git
cd aeonscript/reference
pip install -e .
```

### Encoder un fichier en ADN

```python
from aeonscript import encode_file, decode_oligos

# Encoder un texte en oligos ADN
oligos = encode_file("mon_document.txt")
print(f"Encodé en {len(oligos)} oligos de ~200 bases chacun")
# → Liste de séquences ACGT prêtes à être synthétisées

# Décoder
content = decode_oligos(oligos)
with open("mon_document_decoded.txt", "wb") as f:
    f.write(content)
```

### Démo en ligne de commande

```bash
python reference/examples/encode_demo.py
```

→ Cet exemple encode un court extrait textuel, ajoute des erreurs aléatoires (simulant les erreurs de séquençage), puis vérifie que le décodage correct fonctionne.

---

## Structure du dépôt

```
aeonscript/
├── MANIFESTO.md              # Pourquoi ce projet existe
├── README.md                 # Ce fichier
├── LICENSE                   # MIT (code) + CC-BY-SA (docs)
├── ROADMAP.md                # Feuille de route
├── CONTRIBUTING.md           # Comment contribuer
├── spec/
│   ├── SPEC-v0.1.md          # Spécification technique principale
│   └── layers/               # Détails par couche
├── reference/
│   ├── aeonscript/             # Module Python
│   │   ├── physical.py       # L1 — Encodage binaire → ACGT
│   │   ├── error_correction.py # L4 — Reed-Solomon
│   │   ├── semantic.py       # L5 — Tags sémantiques
│   │   ├── encoder.py        # API haut niveau
│   │   └── decoder.py
│   ├── tests/                # Tests round-trip
│   └── examples/             # Démos exécutables
└── docs/
    └── architecture.md       # Schémas et explications
```

---

## L'architecture en 7 couches (résumé)

| Niveau | Couche | Rôle |
|--------|--------|------|
| L7 | Application | Formats de domaine (PDF-ADN, FASTA-ADN…) |
| L6 | Presentation | Sérialisation, compression, chiffrement |
| L5 | Session | Tags sémantiques, addressage hiérarchique |
| L4 | Transport | Reed-Solomon + LDPC (correction d'erreurs) |
| L3 | Network | Random access par amorces PCR + indexation |
| L2 | Data Link | Multiplexage brins fwd/rev, cadres de lecture |
| L1 | Physical | Alphabet 4-6 lettres, méthylation, contraintes biochimiques |

Détails complets dans [`spec/SPEC-v0.1.md`](spec/SPEC-v0.1.md).

---

## État d'avancement (v0.1)

✅ Manifeste publié
✅ Spec v0.1 rédigée (couches L1, L4, L5 finalisées)
✅ Implémentation Python de référence (L1 + L4 + L5)
✅ Tests round-trip fonctionnels
🔲 Spec couches L2 (multiplexage brin/frame) — en cours
🔲 Spec couche L3 (random access PCR) — en cours
🔲 Port Rust (performance)
🔲 Intégration foundation model (Evo 2) pour codec AI-natif
🔲 Démonstration physique (synthèse + relecture)

---

## Comment contribuer

AeonScript est ouvert à toute contribution. Voir [CONTRIBUTING.md](CONTRIBUTING.md).

Domaines où l'aide est particulièrement précieuse :

- **Bio-informatique** : validation des contraintes biochimiques
- **Théorie de l'information** : optimisation des codes correcteurs cross-layer
- **Foundation models** : intégration de Evo 2 / Caduceus comme codec
- **Rust** : port de performance du codec Python
- **Documentation** : traductions, tutoriels, exemples
- **Standardisation** : aide pour soumission ISO/W3C
- **Sécurité** : audit des protocoles bio-safety

---

## Écosystème

AeonScript est le socle d'une famille de projets ouverts :

| Projet | Rôle | Lien |
|--------|------|------|
| **AeonScript** | Le standard de stockage d'information sur ADN | [aeonscript.org](https://aeonscript.org) |
| **AeonProof** | Coffre-fort de preuves d'authenticité à l'ère des fakes — la crypto détecte, l'ADN archive | [proof.aeonscript.org](https://proof.aeonscript.org) · [repo](https://github.com/aeonscript-spec/aeonproof) |

> AeonProof est bâti sur AeonScript : il grave les preuves d'authenticité (hash + signature + horodatage) dans l'ADN via le format AeonScript.

---

## Licence

- **Code** (`reference/`) : MIT License
- **Documentation** (`MANIFESTO.md`, `spec/`, `docs/`) : Creative Commons CC-BY-SA 4.0

Voir [LICENSE](LICENSE).

---

## Citation

Si vous utilisez AeonScript dans une publication académique :

```bibtex
@misc{aeonscript2026,
  title = {AeonScript: An Open Standard for DNA-Based Information Archival},
  author = {{The AeonScript Contributors}},
  year = {2026},
  url = {https://github.com/<TBD>/aeonscript},
  note = {Version 0.1}
}
```

---

## Contact

- **Discussions** : GitHub Issues
- **Sécurité** : security@aeonscript.org (TBD)
- **Presse / institutionnel** : contact@aeonscript.org (TBD)

---

*« La mémoire de l'humanité ne devrait pas être propriétaire. »*
