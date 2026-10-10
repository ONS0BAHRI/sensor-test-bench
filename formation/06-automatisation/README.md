[Formation](../../README.md) › Module 6

# Module 6 · Automatisation, traçabilité et intégration continue

**Statut :** à faire

Un test fait à la main une fois n'a que peu de valeur. Ce module montre comment le banc enchaîne tous les tests sans intervention, enregistre chaque résultat et vérifie automatiquement chaque modification du code.

## 1. Les niveaux d'automatisation

| Niveau | Mise en œuvre | Fichier |
|---|---|---|
| Exécution | Une procédure par test, enchaînées dans un ordre fixe | [`run_bench.py`](../../run_bench.py), [`tests/test_bench.py`](../../tests/test_bench.py) |
| Configuration | Tous les seuils dans un fichier, aucun seuil dans le code | [`config/limits.yaml`](../../config/limits.yaml) |
| Collecte | Données brutes de chaque test en CSV | `reports/<campagne>/raw/` |
| Traçabilité | Chaque campagne en base : date, mode, numéro de série, firmware, commit Git, verdicts | [`report/database.py`](../../report/database.py) |
| Rapport | HTML autonome avec graphiques, Markdown, JSON | [`report/html_report.py`](../../report/html_report.py) |
| Verdict | OK / KO en couleur, code de sortie 0 ou 1 | `run_bench.py` |
| Intégration continue | Tous les tests à chaque push sur GitHub | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) |

## 2. La séquence de fin de ligne

`run_bench.py` reproduit une séquence de test de production :

1. Ouvrir le banc et lire la version du firmware.
2. Exécuter chaque procédure. **Un test qui plante est noté KO avec son message, et la séquence continue** : on veut le diagnostic complet.
3. Enregistrer les CSV, les graphiques, le rapport et la base.
4. Afficher le verdict global et renvoyer le code de sortie : 0 si conforme, 1 sinon.

Le code de sortie permet d'enchaîner le banc avec d'autres outils (script, séquenceur, intégration continue) sans lire le texte affiché.

## 3. Exemples de rapports

- [Rapport d'un capteur conforme](exemples/rapport_capteur_conforme.html)
- [Rapport d'un capteur défectueux](exemples/rapport_capteur_defectueux.html)
- [Résumé Markdown d'une campagne](exemples/summary_capteur_conforme.md)

Les fichiers HTML s'ouvrent après téléchargement : GitHub affiche leur code source, pas la page.

## 4. Interroger la traçabilité

```sql
-- Les dernières campagnes et leur verdict
SELECT started_at, mode, serial_number, passed, n_failed
FROM campaigns ORDER BY started_at DESC;

-- L'historique du bruit d'un capteur donné
SELECT c.started_at, r.measures_json
FROM results r JOIN campaigns c ON c.run_id = r.run_id
WHERE r.test_id = 'T03' AND c.serial_number = 'MPU-0001';
```

Ouvrez `reports/results.db` avec DB Browser for SQLite, onglet « Exécuter le SQL ».

## 5. L'intégration continue

À chaque `git push`, GitHub Actions exécute dans l'ordre :

1. Les 44 tests pytest (unitaires, protocole, système en simulation).
2. Une campagne complète sur le capteur simulé : elle doit être **OK**.
3. Une campagne sur le capteur défectueux : elle doit être **KO**. Si elle passe, la CI échoue, car un banc qui accepte un mauvais capteur ne fait pas son travail.
4. La publication des rapports en artefacts téléchargeables.

Pour afficher le badge en haut du README, remplacez `<compte>` par votre nom d'utilisateur GitHub dans l'URL du badge.

## 6. Exercices

1. Passez `max_std_g` de T03 à 0,003 dans `limits.yaml`, relancez, puis remettez la valeur d'origine. Notez pourquoi les seuils sont hors du code.
2. Lancez cinq campagnes avec des graines différentes (`--seed 1` à `--seed 5`) et retrouvez-les dans la base SQLite.
3. Faites volontairement échouer un test, poussez sur une branche de travail et observez la CI échouer sur GitHub.

## Vos résultats

> **À compléter :** capture de la CI verte sur GitHub (onglet Actions) et capture d'une requête SQL dans `images/`.

## Checklist

- [ ] Je sais décrire la séquence de `run_bench.py`
- [ ] J'ai interrogé la base SQLite
- [ ] La CI est verte sur GitHub
- [ ] Captures ajoutées

---

[← Module 5 · Tests du capteur](../05-tests-du-capteur/README.md) · [Sommaire](../../README.md) · [Module 7 · Matériel et firmware →](../07-materiel-et-firmware/README.md)
