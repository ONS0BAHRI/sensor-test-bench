> **Modèle de fiche TP.** Copiez ce fichier sous le nom `README.md` dans un nouveau dossier `TPxx-nom/` (avec les sous-dossiers `images/`, `videos/` et `data/`) : les liens fonctionnent une fois le fichier copié.

[Formation](../../../README.md) › [5 · Tests du capteur](../README.md) › TPxx

# TPxx · Nom du test

**Statut :** à faire

| | |
|---|---|
| **Objectif** | Une phrase : ce que le test vérifie. |
| **Procédure** | `txx_nom` dans [`bench/procedures.py`](../../../bench/procedures.py) |
| **Seuils** | section `Txx_nom` de [`config/limits.yaml`](../../../config/limits.yaml) |
| **Modes** | simulation (SIL) et vrai capteur (HIL) |

## 1. Pourquoi ce test

À quelle question d'un client ou d'un ingénieur ce test répond-il ? Pourquoi est-il fait en industrie ?

## 2. Notions à connaître

- Définitions et formules nécessaires pour comprendre le test.

## 3. Conditions de mesure

Position du capteur, état du vibreur, nombre de mesures.

## 4. Méthode

1. Étapes de la procédure, dans l'ordre.

## 5. Le code

<details>
<summary>Voir le code de <code>txx_nom</code></summary>

```python
# copier ici la procédure
```

</details>

## 6. Critère d'acceptation

```yaml
Txx_nom:
  seuil: valeur
```

## 7. Lancer le TP

```bash
pytest tests/test_bench.py -k txx -s
pytest tests/test_bench.py -k txx -s --mode hil --port COM3
```

## 8. Résultat de référence (simulation)

| Mesure | Valeur |
|---|---|

![TPxx en simulation](images/sil.png)

**Lire le graphique.** Ce qu'on doit voir et ce que chaque élément représente.

## 9. Ce qui serait anormal

- Symptôme : cause probable.

## 10. Vos résultats sur le vrai capteur

| Mesure | Simulation | Vrai capteur | Écart / commentaire |
|---|---|---|---|

![TPxx sur le vrai capteur](images/hil.png)

**Analyse :** écarts observés et leur explication.

## 11. Pour aller plus loin

- Variantes et expériences supplémentaires.

## 12. Questions de révision

**Question ?**

<details>
<summary>Réponse</summary>

Réponse.

</details>

## Checklist de fin de TP

- [ ] Test lancé et compris en simulation
- [ ] Test lancé sur le vrai capteur
- [ ] Graphique réel ajouté (`images/hil.png`)
- [ ] Tableau des résultats réels rempli
- [ ] Analyse rédigée
- [ ] Statut mis à jour ici et dans le sommaire

---

[← TP précédent](../README.md) · [Sommaire du module](../README.md) · [TP suivant →](../README.md)
