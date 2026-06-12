# Contribuer à AeonScript

> *"La mémoire de l'humanité ne devrait pas être propriétaire."*

AeonScript est un projet ouvert. Toute personne peut contribuer — programmeur ou non, biologiste ou non, anglophone ou non. Ce document explique **concrètement** ce que vous pouvez faire, en fonction de qui vous êtes.

---

## 🎯 Six façons de contribuer

### 1. Vous êtes développeur (Python, Rust, Go, JS, C++…)

**Effort minimum utile** : 1 PR qui corrige une faute de frappe dans la spec ou la doc.

**Effort plus substantiel** :
- **Implémenter AeonScript dans un nouveau langage**. La référence existe en Python et en Rust. Un port en Go, Java, C++ ou JavaScript serait précieux. Forkez, codez, ouvrez une issue avec le lien.
- **Améliorer le codec de référence** : corriger un bug, accélérer une fonction, ajouter des tests.
- **Construire un outil dérivé** : un GUI desktop, une extension VS Code, un add-on Inkscape, un plug-in BioPython. Pas besoin d'attendre l'autorisation — créez, publiez, dites-le nous.
- **Compiler en WebAssembly** : porter le codec Rust en WASM pour qu'il tourne dans le navigateur, sans serveur.

**Par où commencer** :
1. Cloner le repo et faire tourner les tests existants (`cd reference && pip install -e . && pytest`)
2. Lire [SPEC v0.1](spec/SPEC-v0.1.md) puis [docs/wire-format-by-example.md](docs/wire-format-by-example.md)
3. Ouvrir une [Discussion](https://github.com/aeonscript-spec/aeonscript/discussions) pour expliquer ce sur quoi vous voulez travailler — pour éviter de doublonner avec quelqu'un d'autre

---

### 2. Vous êtes chercheur, ingénieur en théorie de l'information ou biologie computationnelle

**Effort minimum utile** : 1 commentaire de 5 lignes en Discussion sur "voilà ce qui me gêne dans §3.2".

**Effort plus substantiel** :
- **Critiquer la spec normative**. Lire [SPEC v0.1](spec/SPEC-v0.1.md) avec œil expert et ouvrir des issues sur les choix qui ne tiennent pas. Sur la couche Reed-Solomon, sur les contraintes biochimiques L1, sur le format des tags L5 — tout est sur la table.
- **Réviser le draft L2 multiplexing** ([`spec/drafts/L2-multiplexing-draft.md`](spec/drafts/L2-multiplexing-draft.md)). Les 8 questions ouvertes ont besoin de vos voix.
- **Proposer un nouveau profil L4** (HEDGES, DNA Fountain, codec AI-natif). Un draft de spec dans `spec/drafts/L4-<votre-codec>.md` suffit pour démarrer la conversation.
- **Évaluer le profil L1-3-goldman** ([`reference/aeonscript/goldman.py`](reference/aeonscript/goldman.py)) — l'implémentation est-elle fidèle au Goldman 2013 ? Y a-t-il des optimisations qui changeraient la conformance ?

**Par où commencer** :
1. Lire [comparison-vs-alternatives.md](docs/comparison-vs-alternatives.md) — c'est là qu'AeonScript se positionne vs votre travail
2. Si vous êtes auteur d'un papier cité (Goldman, Erlich, Press, Brixi…), nous serions honorés par votre relecture directe : `contact@aeonscript.org`

---

### 3. Vous êtes une équipe de recherche ou une startup DNA storage

**Effort minimum utile** : implémenter le décodeur et vérifier qu'il fait passer les 10 vecteurs canoniques.

**Effort plus substantiel** :
- **Intégrer AeonScript dans votre pipeline existant**, même partiellement (un codec, un profil L1, le format de tag).
- **Faire passer les vecteurs de conformance** ([`spec/test-vectors/vectors-l1-l5.json`](spec/test-vectors/vectors-l1-l5.json)). Si ça marche, publier votre implémentation et l'ajouter à `KNOWN_IMPLEMENTATIONS.md` (créer le fichier dans votre PR).
- **Tester sur ADN physique réel**. Si vous avez une plateforme de synthèse + séquençage, un test physique d'AeonScript v0.1 sur 1 Mo de données serait le résultat le plus précieux qu'on puisse obtenir.
- **Co-publier**. Si vous démontrez quelque chose d'intéressant avec AeonScript, le projet peut être co-signataire d'un papier de méthode.

**Par où commencer** :
1. Cloner le repo et faire tourner les vecteurs de conformance via la CLI : `aeonscript validate spec/test-vectors/vectors-l1-l5.json`
2. Email à `contact@aeonscript.org` pour discuter d'une collaboration formelle

---

### 4. Vous parlez une langue autre que l'anglais ou le français

**Effort minimum utile** : traduire un seul paragraphe du MANIFESTO dans votre langue.

**Effort plus substantiel** :
- **Traduire le MANIFESTO complet** dans votre langue maternelle. Espagnol, portugais, arabe, mandarin, hindi, swahili — toutes les langues comptent et ouvrent l'adoption locale.
- **Traduire la FAQ** ([`FAQ.md`](FAQ.md)) ou le glossaire ([`docs/GLOSSARY.md`](docs/GLOSSARY.md)).
- **Traduire la page d'accueil aeonscript.org** pour qu'elle s'adapte à la langue du visiteur.

**Par où commencer** :
1. Copier `MANIFESTO.md` vers `docs/translations/<langue>/MANIFESTO.md`
2. Traduire en conservant la structure (titres, listes)
3. Ouvrir une PR — même incomplète, on l'accepte

---

### 5. Vous avez un réseau dans les institutions, fondations ou la presse

**Effort minimum utile** : une intro par email entre AeonScript et UNE personne intéressante.

**Effort plus substantiel** :
- **Mettre en relation** AeonScript avec un contact dans une institution de mémoire (BnF, INA, Library of Congress, Internet Archive, archives nationales de votre pays), une fondation (Sloan, Mellon, Wellcome), un programme de recherche public (ERC, NSF, Horizon Europe), ou un journaliste scientifique (Science, Nature, MIT Tech Review, *Le Monde*…).
- **Partager le projet** sur LinkedIn, X/Twitter, dans vos newsletters professionnelles ou vos cercles académiques, avec **votre propre contexte** (ce que ça change pour vous, pour votre domaine).
- **Inviter à une présentation** : si vous organisez un séminaire universitaire, un meet-up tech, une conférence d'archivistes, nous pouvons préparer un talk de 30 minutes.

**Par où commencer** :
1. Lire le [PDF "AeonScript pour tous"](docs/AeonScript-pour-tous.pdf) (français, accessible) — c'est l'outil de partage non-technique
2. Identifier UNE personne dans votre réseau qui devrait connaître ce projet
3. Email à `contact@aeonscript.org` avec en copie cette personne, en lui présentant le projet en 3 lignes

**C'est la contribution la plus puissante qui existe.** Une seule introduction au bon moment vaut six mois de recherche autonome.

---

### 6. Vous êtes une fondation, un programme de financement, un mécène

**Effort minimum utile** : un appel téléphonique de 20 minutes pour comprendre le besoin.

**Effort plus substantiel** : financer une phase de la roadmap. Les besoins concrets actuels :

| Phase | Montant | Livrable mesurable |
|---|---|---|
| **Démo physique** (Phase 3) | ~50 000 € | Synthèse réelle de 1 Mo chez Twist + relecture + papier scientifique publié |
| **Port industriel** (Phase 4) | ~500 000 € | Codec Rust de production + build WASM + CLI multi-plateforme |
| **Standardisation ISO** (Phase 5) | ~2-5 M€ sur 5 ans | Soumission ISO/IEC + fondation à but non lucratif établie |

Chaque tranche débloque la suivante en fonction des livrables. Modèle inspiré de l'ERC Synergy : pas de chèque global, des jalons mesurables.

**Par où commencer** :
1. Lire le [MANIFESTO](MANIFESTO.md) et la [ROADMAP](ROADMAP.md)
2. Email direct à `contact@aeonscript.org` avec sujet "Funding inquiry" — réponse sous 24h, avec une note de 5 pages dédiée à votre programme si pertinent

---

## 🛠️ Pour tous les contributeurs — règles communes

### Communication
- **GitHub Discussions** : questions, idées, débats de design — toujours préférer la discussion publique à l'email privé pour les sujets techniques.
- **GitHub Issues** : bugs, tâches précises, propositions concrètes.
- **Email `contact@aeonscript.org`** : tout ce qui est personnel, institutionnel ou confidentiel.
- **Toujours en bonne foi.** Ce projet adhère au [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) ([CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)).

### Workflow Git
1. Forker, créer une branche depuis `main`
2. Faire vos changements + ajouter les tests si applicable
3. Vérifier que la CI passe localement (`pytest` + `node reference/examples/smoke_test.js`)
4. Ouvrir une PR avec une description claire, en utilisant le template
5. Répondre aux reviews — toute modification est bonne à prendre

### Standards de code
- **Python** : type hints, docstrings, pas de dépendances externes ajoutées sans discussion préalable
- **Rust** : `cargo fmt` + `cargo clippy -- -D warnings`
- **Markdown** : phrases en français OU en anglais (pas mélangées dans un même document), ASCII art toléré

### Tests obligatoires pour les PR de code
- Un test round-trip qui prouve que vos changements n'ont rien cassé
- Si vous touchez la spec (un caractère du wire format), un nouveau test vector

---

## 📜 Licence

- Code (`reference/`, `reference-rs/`) : **MIT**
- Spec et docs (`spec/`, `docs/`, `MANIFESTO.md`, etc.) : **CC-BY-SA 4.0**

En soumettant une PR, vous acceptez que votre contribution soit publiée sous ces licences. Pas de CLA (Contributor License Agreement) requis.

---

## 🙏 Reconnaissance

Tous les contributeurs sont listés dans le fichier [`AUTHORS`](AUTHORS) (à créer dès la première contribution externe) et dans les notes de release. Les contributions substantielles peuvent être créditées dans les publications académiques liées à AeonScript.

---

## ❓ Vous ne savez pas par où commencer ?

C'est normal. Le projet est jeune. Voici la réponse la plus utile :

> **"Faites quelque chose."** Une issue, un commentaire de Discussion, un partage sur LinkedIn, un email à `contact@aeonscript.org` avec votre profil. Ça déclenche une conversation. La conversation produit une voie d'action plus précise. Tout commence par cette première micro-action.

Merci. Vraiment.

— L'équipe AeonScript
