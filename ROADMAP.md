# Feuille de route AeonScript

État au démarrage, mai 2026.

---

## Phase 0 — Fondations (terminée)

- [x] Manifeste publié
- [x] Spec v0.1 — couches L1, L4, L5 finalisées
- [x] Implémentation Python de référence (L1+L4+L5)
- [x] Smoke test Node.js (L1+L5, sans Reed-Solomon)
- [x] Round-trip encode/decode démontré

---

## Phase 1 — Maturation v0.2 (3-6 mois)

### Spec
- [ ] Couche L2 — multiplexage de brins (forward/reverse simultanés)
- [ ] Couche L2 — multiplexage de cadres de lecture (frames +0, +1, +2)
- [ ] Couche L3 — random access par amorces PCR
- [ ] Couche L6 — compression et chiffrement standardisés
- [ ] Format d'index pour la table de fichiers
- [ ] Spec du protocole bio-safety (base de données de hazards)

### Codec
- [ ] Codec Goldman ternary (contraintes structurelles, élimine les runs)
- [ ] Codec RLL-constrained (densité Shannon optimale)
- [ ] LDPC outer code (récupération d'oligos perdus)
- [ ] Hash de méthylation cross-layer (L1-5m)

### Tooling
- [ ] CLI `aeonscript encode/decode/inspect`
- [ ] Validateur de conformité spec
- [ ] Visualisateur d'oligos
- [ ] Benchmarks (densité, vitesse, robustesse aux erreurs)

---

## Phase 2 — Implémentation industrielle (6-12 mois)

- [ ] Port Rust optimisé (performance ×100)
- [ ] Intégration foundation model — Evo 2 comme codec AI-natif
- [ ] Support FASTQ entrée/sortie (compatibilité Illumina/Nanopore)
- [ ] Tests sur 1 Go simulé (genres : texte, image, vidéo, archives)
- [ ] Tests de robustesse : injection d'erreurs réalistes (modèle Twist + Illumina)
- [ ] Package npm + crates.io + PyPI

---

## Phase 3 — Démonstration physique (12-18 mois)

- [ ] Partenariat Twist Bioscience ou IDT pour synthèse
- [ ] Encodage de 1 Mo de contenu réel (ex : *Petit Prince* multilingue)
- [ ] Synthèse, stockage, séquençage (Illumina + Nanopore)
- [ ] Démonstration publique du round-trip physique
- [ ] Publication des données et du protocole en open access

---

## Phase 4 — Adoption institutionnelle (18-36 mois)

- [ ] Pilotes :
  - [ ] Bibliothèque nationale de France (BnF)
  - [ ] Library of Congress
  - [ ] Internet Archive
  - [ ] Smithsonian Institution
  - [ ] UNESCO Memory of the World
- [ ] Création de la Fondation AeonScript (statut association loi 1901 / 501(c)(3))
- [ ] Premiers cas d'usage en production
- [ ] Catalogue de patrimoine encodé

---

## Phase 5 — Standardisation (24-48 mois)

- [ ] Soumission ISO/IEC JTC 1 (Information Technology)
- [ ] Soumission W3C pour les couches d'interopérabilité web
- [ ] Programme de certification "AeonScript Compliant"
- [ ] Suite de tests de conformité
- [ ] Spec v1.0 stable

---

## Phase 6 — Écosystème (continu)

- [ ] Intégration data centers (cold storage tier)
- [ ] Adoption par les fabricants de séquenceurs (presets AeonScript)
- [ ] Adoption par les fabricants de synthétiseurs (kit AeonScript)
- [ ] Support dans les outils bio-informatiques (samtools, bcftools, etc.)
- [ ] Marketplace de "blocs" — partage de patrimoine encodé

---

## Limitations connues de v0.1

Ces points sont explicitement reportés à v0.2 :

1. **Contraintes L1 relâchées** : MAX_HOMOPOLYMER=8 et GC ∈ [25%, 75%] vs. les valeurs cibles 3 et [40%, 60%]. Le codec 2-bit naïf ne peut pas garantir mieux ; nécessite Goldman ternary ou RLL.
2. **Pas de multiplexage** : couche L2 entièrement absente. Densité limitée à ~1.5-1.8 bits/base utiles vs. cible 4+ bits/base.
3. **Pas de random access** : pour relire, il faut décoder TOUS les oligos. La couche L3 (amorces PCR) résout ça.
4. **Tag parsing minimal** : pas d'échappement de `;` et `=` dans les valeurs. Encodeur fait du strip défensif sur les MIME.
5. **Pas de hash cross-layer** : profile L1-5m (méthylation) non implémenté.
6. **Bio-safety stub** : le filtrage de pathogènes est documenté mais pas implémenté.
7. **Pas de support binaire complet** : testé sur texte UTF-8 et bytes aléatoires ; à étendre formellement à fichiers image/vidéo.

---

## Métriques cibles par phase

| Métrique | v0.1 | v0.2 | v1.0 |
|------|------|------|------|
| Densité utile (bits/base) | ~1.5 | ~2.5 | ~4 |
| Robustesse (% erreurs corrigées) | 0 | 6% par bloc | 16% par bloc |
| Random access | non | non | oui |
| Multiplexage | non | brin uniquement | brin + frame |
| Conformité industrielle | partielle | bonne | totale |
| Performance Python | ~10 ko/s | ~100 ko/s | n/a |
| Performance Rust | n/a | ~10 Mo/s | ~100 Mo/s |

---

## Comment contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md).

Les contributions les plus prioritaires aujourd'hui :

1. **Implémenter Goldman ternary** dans `physical.py` (élimine la relaxation des contraintes)
2. **Reviewer le Reed-Solomon** dans `error_correction.py`
3. **Écrire le validateur de conformité** spec
4. **Démarrer le port Rust** du module physical
5. **Rédiger les détails de couches L2/L3**
