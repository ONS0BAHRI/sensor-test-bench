[Formation](../../../README.md) › [5 · Tests du capteur](../README.md) › TP11

# TP11 · Dérive thermique

**Statut :** à faire

| | |
|---|---|
| **Objectif** | Mesurer la variation de l'offset avec la température. |
| **Procédure** | à écrire : `t11_derive_thermique` dans [`bench/procedures.py`](../../../bench/procedures.py) |
| **Modes** | vrai capteur uniquement |

## 1. Pourquoi ce test

Un capteur embarqué subit des variations de température. Si son zéro dérive avec la chaleur, la mesure devient fausse. Les fiches techniques donnent cette dérive en mg/°C.

## 2. Notions à connaître

- Dérive thermique : variation lente d'une caractéristique (offset, gain) avec la température.
- Coefficient de température : pente de la droite offset = f(température), en mg/°C.
- Le MPU6050 a un capteur de température interne (registres 0x41-0x42) : température en °C = brut / 340 + 36,53.

## 3. Conditions de mesure

Capteur à plat, immobile. Chauffe douce avec un sèche-cheveux, à distance, sans dépasser 50 à 60 °C, puis refroidissement naturel.

## 4. Méthode

1. Placer le capteur à plat et lancer des acquisitions répétées (par exemple 500 mesures toutes les 5 s pendant 10 min).
2. Chauffer doucement pendant les premières minutes, puis laisser refroidir.
3. Pour chaque acquisition : moyenne de X, Y, Z et de la température.
4. Tracer l'offset en fonction de la température et calculer la pente par régression linéaire.

## 5. Implémentation à réaliser

Ce TP n'est pas encore codé : c'est un exercice complet de conception de test. Les étapes :

1. Ajouter une section `T11_derive_thermique` dans `config/limits.yaml` (nombre d'acquisitions, intervalle, pente maximale en mg/°C).
2. Écrire `t11_derive_thermique(bench, lim)` dans `bench/procedures.py`, sur le modèle de `t06_repetabilite` : boucle d'acquisitions, moyenne de X et de `temp`, puis `sp.linear_fit(temperatures, offsets)`.
3. L'ajouter à `ALL_PROCEDURES` (après `t10_echantillonnage`).
4. Ajouter `plot_T11` dans `report/plots.py` : offset en fonction de la température, avec la droite de régression.
5. Lancer `python run_bench.py --mode hil --port COM3 --docs` : le graphique est rangé dans `images/hil.png`.

## 6. Ce qui serait anormal

- Une boucle entre la chauffe et le refroidissement : le capteur interne et la puce n'ont pas la même température au même moment (inertie thermique).

## 7. Vos résultats sur le vrai capteur

> **À compléter** après la campagne sur le matériel. Ajoutez le graphique, remplissez le tableau et écrivez votre analyse.

**Ce à quoi s'attendre.** Ce TP n'a de sens que sur le vrai capteur : le simulateur ne modélise pas la dérive thermique.

<!-- Après la campagne réelle, retirez cette ligne de commentaire et la dernière pour afficher le graphique :
![TP11 sur le vrai capteur](images/hil.png)
-->

**Analyse :** *(Que montrent vos mesures ? Quels écarts avec la simulation, et pourquoi ? Le défaut vient-il du capteur ou du banc ?)*

## 8. Pour aller plus loin

- Ajoutez une dérive thermique au simulateur (paramètre en mg/°C) pour pouvoir tester votre procédure en mode SIL.
- Comparez la pente obtenue à la valeur de la datasheet.

## 9. Questions de révision

**Pourquoi chauffer doucement ?**

<details>
<summary>Réponse</summary>

Pour que la température soit homogène dans la puce et éviter d'endommager le module. Une chauffe brutale crée des écarts entre le capteur de température et le reste de la puce.

</details>

**Comment compenser une dérive thermique ?**

<details>
<summary>Réponse</summary>

En mesurant la température en même temps et en corrigeant l'offset avec le coefficient trouvé : offset corrigé = offset − coefficient × (T − T_référence).

</details>

## Checklist de fin de TP

- [ ] Procédure, seuils et graphique implémentés
- [ ] Test lancé sur le vrai capteur
- [ ] Graphique réel ajouté (`images/hil.png`) et affiché ci-dessus
- [ ] Tableau des résultats réels rempli
- [ ] Analyse rédigée
- [ ] Statut mis à jour ici et dans le [sommaire](../../../README.md#parcours)

---

[← TP10](../TP10-echantillonnage/README.md) · [Sommaire du module](../README.md) · [TP12 →](../TP12-robustesse/README.md)
