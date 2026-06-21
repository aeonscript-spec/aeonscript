# AeonScript — Protocole de démonstration physique (ADN réel)

**Objectif** : encoder un contenu réel avec AeonScript, le **synthétiser en ADN**, le stocker, le **reséquencer**, le décoder, et prouver qu'il est récupéré **bit pour bit**. Puis publier le résultat.

**Statut** : protocole prêt à exécuter — en attente de financement (~Phase 3 de la roadmap).
**Version** : v0.1 · juin 2026

> Ce document est exécutable tel quel par toute équipe disposant d'un accès à un fournisseur de synthèse d'oligos et à un séquenceur. Les coûts sont des estimations 2026, à confirmer par devis.

---

## 1. Deux paliers (choisir selon le budget)

| Palier | Contenu encodé | Oligos (~200 b) | Coût synthèse | Coût séquençage | Total indicatif |
|--------|----------------|-----------------|---------------|-----------------|-----------------|
| **A — Preuve minimale** | ~10 Ko (manifeste texte) | ~250 | 200 – 600 € | service ~300 € | **~0,5 – 1 k€** |
| **B — Publication** | ~1 Mo (texte + image + audio) | ~25 000 | 1,5 – 4 k€ | 1 run iSeq ~1 k€ | **~3 – 6 k€** |

Recommandation : commencer par le **palier A** (preuve de concept publiable, risque financier minimal), puis B pour le papier.

---

## 2. Vue d'ensemble du pipeline

```
[1] Contenu réel  ──encode AeonScript──►  pool d'oligos (FASTA)
[2] Design du pool : amorces PCR, contraintes fournisseur, contrôle qualité in-silico
[3] Synthèse          (Twist / IDT — pool d'oligos sur puce)
[4] Stockage          (lyophilisation, conservation à sec / -20 °C)
[5] Amplification PCR  (récupération du pool)
[6] Séquençage         (Illumina iSeq/MiSeq ou Oxford Nanopore)
[7] Reconstruction     (consensus par oligo, décodage AeonScript)
[8] Vérification       (hash SHA-256 identique à l'original ?)  →  publication
```

---

## 3. Étape par étape

### Étape 1 — Encodage
- Choisir le contenu (palier A : `MANIFESTO.md` ; palier B : + un logo PNG + un court extrait audio WAV).
- Encoder avec la référence : `aeonscript encode contenu.bin -o pool.fasta` (CLI Python) ou `encode_file`.
- Paramètres : profil **L1-4**, codec **L4 = rs255-223** (Reed-Solomon obligatoire ici — la lecture ADN a un taux d'erreur réel ~0,1–1 %/base).
- **Sortie** : un fichier FASTA d'oligos, chacun ≤ 200 bases, avec l'étiquette AeonScript en tête de bloc.

### Étape 2 — Design du pool (in-silico, avant de payer)
- **Amorces PCR** : ajouter à chaque oligo une paire d'amorces communes de 20 bases (5′ et 3′) pour l'amplification/le random access. Les exclure du payload (elles sont retirées au décodage).
- **Contrôles qualité automatiques** (script à écrire, `tools/pool-qc.py`) :
  - GC ∈ [40 %, 60 %] par oligo (resserrer vs la tolérance v0.1 pour la synthèse)
  - homopolymères ≤ 4 (exigence synthèse réelle, plus stricte que v0.1)
  - pas de structures secondaires fortes (ΔG) ni de répétitions inter-oligos
  - unicité des amorces vs le payload
- **Si des oligos échouent** le QC : re-scrambler (graine alternative) ou activer le profil **L1-3-goldman** (élimine structurellement les homopolymères).
- **Bio-safety (SPEC §9)** : passer le pool complet au crible IGSC avant commande. Refuser toute correspondance pathogène.

### Étape 3 — Synthèse
- **Fournisseur** : Twist Bioscience (Oligo Pools) ou IDT (oPools). Format : pool d'oligos synthétisés sur puce, livré lyophilisé.
- **Spécifier** : longueur, nombre d'oligos, le FASTA, l'échelle (la plus basse suffit : on a besoin de copies, pas de masse).
- **Délai** : ~2–3 semaines.

### Étape 4 — Stockage
- Conserver le pool **lyophilisé, à sec**, à -20 °C pour la démo (température ambiante possible mais -20 °C = marge).
- Pour démontrer la durabilité : en option, encapsuler une fraction dans des billes de silice (DNAshell / Imagene) → preuve de conservation longue durée.

### Étape 5 — Amplification
- Réhydrater, amplifier par **PCR** avec les amorces communes (et amorces spécifiques si on teste le random access par bloc).
- Vérifier sur gel / Bioanalyzer la taille attendue (~240 bases avec amorces).

### Étape 6 — Séquençage
- **Option économique** : service de séquençage (envoyer le pool, recevoir les FASTQ).
- **Option interne** : Illumina **iSeq 100** (~run 1 k€) ou **MiSeq** ; ou **Oxford Nanopore MinION** (portable, ~1 k€ l'appareil).
- **Couverture cible** : ≥ 30× par oligo (sur-séquencer pour le consensus — c'est gratuit en lecture, et ça écrase les erreurs).
- **Note Nanopore** : taux d'indels plus élevé → prévoir le profil L4-HEDGES (roadmap v0.2) ou rester sur Illumina pour la première démo.

### Étape 7 — Reconstruction
- Démultiplexer par amorces, regrouper les lectures par oligo.
- **Consensus par position** (vote majoritaire) sur chaque oligo → corrige la majorité des erreurs de lecture *avant même* le Reed-Solomon.
- Retirer les amorces, réassembler les blocs via l'**étiquette AeonScript** (champ `ID`, ordre).
- Décoder : `aeonscript decode pool.fasta -o recovered.bin`. Le Reed-Solomon rattrape les erreurs résiduelles.

### Étape 8 — Vérification & publication
- **Critère de succès dur** : `sha256(recovered.bin) == sha256(original.bin)`. Identité bit pour bit, sinon l'essai a échoué.
- Mesurer : taux d'erreur brut/base, nombre d'oligos perdus, erreurs corrigées par RS, marge restante.
- **Publier** : protocole + données brutes (FASTQ) + hashes + code, en open access. Soumettre en note de méthode (bioRxiv, puis revue).

---

## 4. Budget d'erreur (pourquoi ça marche)

Trois filets superposés, du plus fin au plus grossier :

1. **Sur-séquençage + consensus** : 30× de couverture → l'erreur aléatoire par position s'efface par vote.
2. **Reed-Solomon RS(255,223)** : corrige jusqu'à 16 octets erronés par bloc de 255 — rattrape ce que le consensus a laissé.
3. **(v0.2) LDPC inter-oligos** : récupère des oligos entièrement perdus (échec de synthèse/PCR d'un oligo).

Pour la démo v0.1, les filets 1 + 2 suffisent largement à un round-trip parfait sur Illumina.

---

## 5. Calendrier indicatif (palier A)

| Semaine | Activité |
|---------|----------|
| S1 | Encodage + design du pool + QC in-silico + bio-safety + devis |
| S2 | Commande synthèse |
| S2–S4 | Attente synthèse |
| S5 | Réception, réhydratation, PCR, contrôle |
| S5–S6 | Séquençage |
| S6 | Reconstruction, décodage, vérification |
| S7 | Rédaction + publication des données |

→ **~6–7 semaines** du feu vert à la preuve publiée.

---

## 6. Risques & parades

| Risque | Parade |
|--------|--------|
| Oligos échouent le QC synthèse | re-scramble / profil Goldman / resserrer les contraintes |
| Biais de synthèse (oligos sous-représentés) | sur-séquencer, RS + (v0.2) LDPC |
| Indels Nanopore | rester Illumina pour la v0.1, ou L4-HEDGES en v0.2 |
| Coût supérieur au devis | commencer au palier A, échelle de synthèse minimale |
| Contamination / dégradation | aliquotes, stockage -20 °C, témoins |

---

## 7. Ce que cette démo prouve

- AeonScript n'est pas qu'un format papier : il **survit à un aller-retour dans la matière réelle**.
- Le pipeline complet **encode → molécule → relecture → décode** rend l'original **à l'identique**.
- La preuve passe le projet de « spec crédible » à « technologie démontrée » — le jalon qui débloque l'adoption et le financement de la suite.

---

## 8. Pré-requis pour lancer

- [ ] Budget palier A (~0,5–1 k€) ou B (~3–6 k€)
- [ ] Compte fournisseur synthèse (Twist / IDT)
- [ ] Accès séquençage (service ou appareil)
- [ ] Script `tools/pool-qc.py` (à écrire — design + QC du pool)
- [ ] Accès à une base de criblage bio-safety (IGSC ou équivalent)

> Dès que le budget et l'accès labo sont là, ce protocole se déroule sans décision supplémentaire. C'est précisément le livrable que cherche un financeur : un plan exécutable, chiffré, à jalons.
