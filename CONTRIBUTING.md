# Contribuer à AeonScript

Merci de votre intérêt. AeonScript est un projet ouvert ; toute personne peut contribuer, sans exception.

---

## Comment commencer

### 1. Comprendre le projet

Lire dans l'ordre :
1. [MANIFESTO.md](MANIFESTO.md) — pourquoi le projet existe
2. [README.md](README.md) — vue d'ensemble technique
3. [spec/SPEC-v0.1.md](spec/SPEC-v0.1.md) — spécification technique courante
4. [ROADMAP.md](ROADMAP.md) — où on va

### 2. Faire tourner la démo

**Avec Node.js (rapide, démontre L1+L5)** :
```bash
cd reference
node examples/smoke_test.js
```

**Avec Python (référence complète L1+L4+L5)** :
```bash
cd reference
pip install -e .
python examples/encode_demo.py
pytest tests/
```

### 3. Choisir un domaine

Les contributions sont organisées par couches de la spec :

| Couche | Domaine | Compétences utiles |
|------|------|------|
| L1 — Physique | Encodage binaire ↔ DNA, contraintes biochimiques | Codage de canal, bioinfo |
| L2 — Liaison | Multiplexage brins, frames | Optimisation combinatoire |
| L3 — Réseau | Random access PCR | Algorithmique, bio-moléculaire |
| L4 — Transport | Reed-Solomon, LDPC | Théorie des codes |
| L5 — Session | Tags sémantiques, addressage | Formats, parsers |
| L6 — Présentation | Compression, chiffrement | Crypto, compression |
| L7 — Application | Formats domaine (PDF, IIIF…) | Standards documents |
| Bio-safety | Filtrage pathogènes | Bio-sécurité, hazard databases |
| Tooling | CLI, validateurs | DevOps |

---

## Workflow de contribution

### Bugs

1. Ouvrir une **issue** GitHub décrivant :
   - Ce que vous attendiez
   - Ce qui s'est passé
   - Reproduction minimale (séquence ADN, commande, version)
2. Si vous pouvez corriger : ouvrir une **pull request** liée à l'issue.

### Améliorations de spec

1. Ouvrir une **issue** de type `spec-discussion`
2. Décrire le problème actuel et la proposition
3. Attendre la discussion communauté (≥ 1 semaine)
4. Si consensus, soumettre une PR sur `spec/SPEC-v0.X.md`

### Nouvelles couches / fonctionnalités

1. Lire la `ROADMAP.md` pour vérifier que c'est prioritaire
2. Ouvrir une issue de design
3. Coder dans une branche de feature
4. Tests obligatoires (round-trip + propriétés)
5. PR avec documentation à jour

---

## Standards de code

### Python (`reference/aeonscript/`)
- Python 3.10+
- Type hints obligatoires
- Docstrings au format Google ou NumPy
- Pas de dépendances externes pour le cœur du codec
- `pytest` pour les tests
- Format : `black` + `ruff`

### JavaScript (`reference/examples/*.js`)
- Node.js 18+
- ES modules ou CommonJS — au choix selon contexte
- Pas de framework, code "vanilla"

### Rust (à venir)
- Stable Rust
- `cargo fmt` + `cargo clippy -- -D warnings`
- Couverture de tests > 80%

---

## Tests

Toute PR qui modifie le codec doit inclure :

1. **Round-trip test** : encode → decode = identité, sur ≥ 3 tailles différentes
2. **Property test** : pour chaque modification de couche, vérifier que la propriété invariant est préservée
3. **Constraint test** : vérifier que tous les oligos émis respectent les contraintes L1
4. **Si applicable** : test d'erreurs injectées

Exemple :
```python
def test_my_new_feature():
    original = b"some bytes"
    oligos = encode_bytes(original, ...)
    assert decode_oligos(oligos) == original
```

---

## Revue de code

Les PR sont revues sur :

1. **Correction** — tests passent, pas de régression
2. **Adhérence à la spec** — code conforme à `SPEC-v0.X.md`
3. **Simplicité** — préférer simple à clever
4. **Documentation** — code commenté + docs mises à jour
5. **Tests** — couverture des cas

Tout reviewer peut demander modifications. Les mainteneurs ont l'autorité de fusion.

---

## Communication

- **GitHub Discussions** — questions, idées, discussions de spec
- **GitHub Issues** — bugs, tâches, propositions concrètes
- **Mailing list** (à créer) — annonces, RFC
- **Slack/Discord** (à créer) — discussions temps réel

---

## Gouvernance

À ce stade (v0.1) le projet est encore informel. La gouvernance formelle s'établira en Phase 4 (cf. ROADMAP) avec la création de la Fondation AeonScript.

En attendant :
- **Décisions techniques** : consensus sur GitHub Issues (≥ 3 reviewers)
- **Décisions de spec** : RFC public sur 2 semaines minimum
- **Litiges** : escalade vers les mainteneurs initiaux

---

## Code de conduite

AeonScript adhère au [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

Résumé : respect mutuel, focus sur les arguments techniques et non sur les personnes, accueil de toutes contributions sincères.

---

## Licence et droits

- Toute contribution au **code** sera intégrée sous **MIT License**.
- Toute contribution à la **documentation** sera intégrée sous **CC-BY-SA 4.0**.
- En soumettant une PR, vous certifiez avoir le droit de soumettre ce travail sous ces licences.

Pas de CLA (Contributor License Agreement) requis — la simple soumission de PR vaut acceptation.

---

## Reconnaissance

Les contributeurs sont listés dans le fichier `AUTHORS` (à créer) et dans les notes de release.

Les contributions substantielles peuvent être créditées dans les futures publications académiques liées à AeonScript.

---

*Merci de bâtir avec nous le standard d'archivage de l'humanité.*
