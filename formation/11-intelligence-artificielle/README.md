[Formation](../../README.md) › Module 11

# Module 11 · Intelligence artificielle

**Statut :** à développer

Les tests classiques comparent un indicateur à un seuil. L'apprentissage automatique peut repérer des défauts plus subtils, ou combiner plusieurs indicateurs. Ce module est un projet à construire : il s'appuie sur le détecteur à règles du TP13, qui sert de référence.

**Principe :** l'IA complète les critères OK / KO, elle ne les remplace pas. Un banc de test doit rester explicable.

## 1. Les deux objectifs

| Objectif | Méthode | Type d'apprentissage | Bibliothèque |
|---|---|---|---|
| A. Repérer un signal inhabituel | Isolation Forest | Non supervisé : apprend à partir de signaux sains seulement | scikit-learn |
| B. Dire quel défaut est présent | Random Forest | Supervisé : apprend à partir de signaux étiquetés | scikit-learn |

## 2. Les données

Le simulateur et la fonction `inject_fault` produisent autant de signaux étiquetés que nécessaire : c'est l'avantage d'avoir commencé par la simulation.

| Classe | Génération |
|---|---|
| sain | `bench.read(n)` avec différentes graines (`seed`) |
| pic, saturation, figé, dérive, bruit fort | `inject_fault(signal_sain, défaut, fs)` |

Visez plusieurs centaines de fenêtres par classe, avec des amplitudes de défaut variées (sinon le problème est trop facile).

## 3. Les caractéristiques

Un modèle ne travaille pas sur 2 000 échantillons bruts, mais sur quelques caractéristiques calculées par fenêtre :

| Caractéristique | Ce qu'elle capte |
|---|---|
| Moyenne, écart-type, RMS | Niveau et bruit |
| Minimum, maximum, écart crête à crête | Pics, saturation |
| Kurtosis | Présence de valeurs extrêmes |
| Bruit par différences successives | Bruit fort, capteur figé |
| Pente de régression | Dérive |
| Énergie dans quelques bandes de la FFT | Vibrations, bruit coloré |

## 4. Étapes

1. Créer `ai/dataset.py` : génération des signaux et calcul des caractéristiques, enregistrement en CSV.
2. Créer `ai/train.py` : séparation entraînement / test (80 / 20), entraînement des deux modèles, sauvegarde avec `joblib`.
3. Évaluer : précision, rappel, matrice de confusion pour B ; taux de fausses alarmes sur signaux sains pour A.
4. Comparer au détecteur à règles du TP13, sur les mêmes données.
5. Valider sur le vrai capteur : signaux sains réels, puis défauts provoqués (capteur tapoté, faux contact, chauffe).
6. Ajouter un TP14 « score d'anomalie » à la suite de tests, avec un seuil dans `limits.yaml`.

## 5. Bonus : IA embarquée

Avec Edge Impulse ou TensorFlow Lite Micro, un petit modèle de classification des vibrations peut tourner directement sur l'ESP32.

## Vos résultats

> **À compléter :** matrice de confusion (`images/matrice_confusion.png`), tableau des métriques, comparaison avec le détecteur à règles, résultats sur le vrai capteur.

| Modèle | Précision | Rappel | Fausses alarmes |
|---|---|---|---|
| Règles (TP13) | | | |
| Isolation Forest | | | |
| Random Forest | | | |

## Checklist

- [ ] Jeu de données généré
- [ ] Deux modèles entraînés et évalués
- [ ] Comparaison avec les règles du TP13
- [ ] Validation sur le vrai capteur
- [ ] TP14 intégré à la suite de tests

---

[← Module 10 · Outils industriels](../10-outils-industriels/README.md) · [Sommaire](../../README.md) · [Module 12 · Démo et présentation →](../12-demo-et-presentation/README.md)
