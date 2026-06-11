# Manifeste AeonScript

**Un standard ouvert pour archiver l'humanité dans l'ADN.**

Version 0.1 · Mai 2026

---

## 1. Le constat

L'humanité produit aujourd'hui plus de **120 zettaoctets** de données par an. Nous n'en stockons que ~10 %. Le reste est perdu — ou pire, illisible dans 50 ans parce qu'aucun lecteur ne saura plus ouvrir nos formats actuels.

Trois faits convergent en 2026 :

1. **L'ADN est devenu un support de stockage industrialisé.** Twist Bioscience synthétise 30 millions d'oligos par jour. Microsoft a démontré un pipeline entièrement automatisé. Catalog encode Wikipedia entière en quelques semaines.

2. **Les modèles de fondation génomiques sont arrivés à maturité.** Evo 2 (Arc Institute, 2026) modélise l'ADN à résolution nucléotidique sur 1 Mbp de contexte. Caduceus, HyenaDNA, Nucleotide Transformer poursuivent. Pour la première fois, des IA *comprennent* la grammaire multi-couches du génome.

3. **Aucun standard ouvert n'existe.** Chaque acteur invente son propre codec. Un fichier Microsoft ne se lit pas par Catalog. Twist verrouille ses amorces. Le marché est en train de se figer dans un fragmentation propriétaire — exactement comme l'informatique entre 1975 et 1990.

**La fenêtre est ouverte. Elle se referme dans 5 ans.**

---

## 2. Le problème que AeonScript résout

> Comment garantir qu'un fichier ADN écrit en 2030 par une bibliothèque française sera lisible en 2230 par une archive distribuée, sans manuel d'utilisation externe, sans dépendance à un fournisseur précis, sans clef perdue ?

Aucune solution actuelle ne répond à cette question. AeonScript est conçu pour y répondre.

---

## 3. La vision

AeonScript est :

- **Un standard ouvert** publié sous licence CC-BY-SA, gouverné par une fondation neutre.
- **Une architecture en couches** inspirée du modèle OSI, séparant proprement la physique (alphabet, méthylation), le transport (correction d'erreurs), la session (adressage), et l'application (formats).
- **Auto-descriptif** : chaque bloc commence par un tag sémantique qui décrit son propre codec, sa version, son type de contenu, ses droits d'accès.
- **AI-natif** : l'encodage exploite les modèles de fondation génomique pour atteindre 80-90 % de la borne Shannon, contre ~75 % pour les codes algorithmiques classiques.
- **Multi-tier** : conçu pour être lu à trois vitesses (Illumina rapide / Nanopore profond / PCR sélective).
- **Bio-safe** : intègre dès la spec un protocole de filtrage des séquences pathogènes.

---

## 4. Les sept principes fondateurs

### Principe 1 — L'ouverture sans condition
Toute personne doit pouvoir lire la spec, implémenter un encodeur, et le distribuer. Pas de royalty. Pas de NDA. Pas de "tier premium".

### Principe 2 — La compatibilité temporelle
Un fichier AeonScript v1.0 doit rester décodable par un lecteur v9.0 dans 200 ans. Le format embarque sa propre documentation.

### Principe 3 — La séparation des préoccupations
Sept couches indépendantes (cf. SPEC). Changer la chimie de synthèse ne casse pas le format applicatif. Améliorer le codec n'invalide pas les archives.

### Principe 4 — La densité par superposition
S'inspirer du génome : multiplexage de brins, multiplexage de cadres de lecture, méthylation comme canal métadonnées. Viser 4 bits utiles/base au lieu des 1,5 actuels.

### Principe 5 — L'intégrité par défaut
Codes correcteurs croisés (Reed-Solomon + LDPC + hash dans la méthylation). Pas de corruption silencieuse possible.

### Principe 6 — La biosécurité dès la conception
Tout encodeur certifié AeonScript filtre les séquences contre une base de pathogènes connus avant synthèse. Pas de "kill switch" *a posteriori* — interdiction *a priori*.

### Principe 7 — La gouvernance par les usagers
Bibliothèques nationales, archives, universités, fondations culturelles décident — pas Microsoft, pas Twist, pas Google.

---

## 5. Pourquoi maintenant — et pourquoi ouvert

### Pourquoi maintenant

- 2026-2030 est la fenêtre où le marché du stockage ADN se structure. Après, les positions sont prises.
- Les briques techniques (foundation models, Nanopore, synthèse 5mC) sont *toutes* mûres en 2026, *aucune* ne l'était en 2022.
- Aucun standard ouvert n'existe — la place est vide.

### Pourquoi ouvert

- Le stockage ADN concerne l'archive de l'humanité. Pas un produit commercial.
- Les bibliothèques publiques, les archives nationales, les institutions de mémoire n'achèteront jamais un format propriétaire — elles ont 2000 ans d'expérience qui leur enseigne le contraire.
- L'histoire de l'informatique le prouve : TCP/IP a battu DECnet, HTML a battu Gopher, PDF a battu PostScript propriétaire. Les standards ouverts gagnent toujours sur l'horizon de 20 ans.

---

## 6. Les cas d'usage prioritaires

### A. Préservation culturelle
- Archives nationales (BnF, Library of Congress, INA…)
- Musées (œuvres numérisées haute résolution)
- Langues en voie d'extinction (~90 % des langues humaines disparaissent ce siècle)
- Patrimoine immatériel (musiques, contes oraux, savoir-faire)

### B. Stockage scientifique long terme
- Données génomiques (>2 zettaoctets attendus en 2030)
- Données d'observation astronomique
- Imagerie médicale historique
- Archives climatiques

### C. Archive civilisationnelle distribuée
- Backup de la civilisation contre risques systémiques (catastrophes, cyberattaques, EMP)
- Dépôt mondial multi-sites (style Svalbard Seed Vault, mais pour l'information)

### D. Data centers décarbonés
- Migration du stockage "froid" (60-80 % du total) vers ADN
- Économie potentielle : 1-2 % de l'électricité mondiale

---

## 7. Ce que AeonScript N'EST PAS

- **Pas un produit commercial.** Aucune entité ne vend AeonScript. C'est un protocole.
- **Pas un format propriétaire.** Pas de brevet bloquant, pas de clause non-compete.
- **Pas un remplacement du SSD ou du HDD.** Le stockage chaud reste sur silicium. AeonScript cible l'archive froide >10 ans.
- **Pas un outil de bio-ingénierie offensive.** Aucune génération de pathogènes possible (couche de safety obligatoire).
- **Pas un projet académique isolé.** Conçu dès le départ pour adoption industrielle et standardisation ISO/W3C.

---

## 8. Modèle de gouvernance

### Phase 0 (2026-2027) — Initiative ouverte
- Spec rédigée publiquement sur GitHub
- Code de référence en Rust et Python
- Discussions ouvertes (mailing list + forum)
- Pas de fondation formelle encore

### Phase 1 (2027-2029) — Fondation AeonScript
- Création d'une fondation à but non lucratif (modèle Mozilla / Linux Foundation)
- Conseil d'administration : ≥ 60 % institutions publiques (bibliothèques, universités, États)
- Financement par dotation philanthropique + cotisations industrielles modérées

### Phase 2 (2029+) — Standardisation
- Soumission ISO / IEC
- Soumission W3C pour les couches d'interopérabilité web
- Implémentations certifiées (label "AeonScript Compliant")

---

## 9. Feuille de route synthétique

| Phase | Durée | Livrables |
|------|------|------|
| **P0 — Manifeste & spec v0.1** | 6 mois | Document de spec, code de référence Python, livre blanc |
| **P1 — Implémentation industrielle** | 12 mois | Codec Rust optimisé, intégration Nanopore, encodage 1 Go testé |
| **P2 — PoC physique** | 18 mois | 1 Mo réellement synthétisé chez Twist + relu, démonstration publique |
| **P3 — Partenariats** | 12 mois | Pilotes BnF / Internet Archive / Smithsonian / UNESCO |
| **P4 — Standardisation** | 18 mois | Soumission ISO/IEC, W3C |
| **P5 — Adoption** | continu | Industrialisation, certification, écosystème |

Coût estimé Phase 0-4 : **~5 M€ sur 5 ans** (ordre de grandeur d'une seule subvention ERC Advanced ou d'un round seed startup).

---

## 10. Appel

AeonScript appartient à toute personne ou institution qui croit que la mémoire de l'humanité ne devrait pas être propriétaire.

Si vous êtes :

- **Bibliothécaire, archiviste, conservateur** — votre profession est la mémoire. AeonScript est votre outil.
- **Chercheur en biologie, en information theory, en cryptographie** — nous avons besoin de vous pour finaliser les couches techniques.
- **Ingénieur logiciel** — l'implémentation de référence en Python existe (voir `/reference/`). Le port Rust est ouvert à contribution.
- **Décideur public, mécène, fondation** — c'est l'un des projets les plus levier-able du XXIᵉ siècle. Un investissement de 5 M€ peut shaper la mémoire numérique mondiale pour les 200 prochaines années.
- **Citoyen** — partagez. C'est ainsi qu'un standard ouvert devient inévitable.

---

## Outreach targets (Phase 1)

*Honnêteté préalable : aucune de ces institutions n'a encore été contactée
au moment de la publication v0.1. Cette liste explicite **les institutions
que ce projet cherche à engager** durant la Phase 1 de la roadmap (2026-2027).
Elle est aspirationnelle. Une institution apparaissant ici ne signifie ni
endorsement, ni partenariat, ni même prise de contact préalable — juste
une cible de dialogue.*

- Arc Institute (auteurs Evo 2)
- European Bioinformatics Institute (EMBL-EBI)
- Internet Archive (Brewster Kahle)
- Wikimedia Foundation
- Bibliothèque nationale de France
- Library of Congress
- UNESCO Memory of the World Programme
- CNRS / INRIA
- Mozilla Foundation

---

## Licence du manifeste

Ce manifeste est publié sous **Creative Commons CC-BY-SA 4.0**. Vous pouvez le partager, le traduire, l'adapter, à condition de citer l'origine et de partager sous la même licence.

La spécification technique et le code de référence sont publiés sous **MIT License** (cf. `LICENSE`).

---

*Rédigé en mai 2026. Première version. Toutes les critiques sont les bienvenues — c'est ainsi que vivent les standards ouverts.*
