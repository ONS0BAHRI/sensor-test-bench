[Formation](../../README.md) › Module 8

# Module 8 · Première campagne réelle et comparaison avec la simulation

**Statut :** à faire

Ce module lance la campagne complète sur le vrai capteur, range les graphiques dans chaque TP et compare les résultats à la simulation. Expliquer les écarts est le cœur du métier de testeur.

## 1. Lancer la campagne réelle

```bash
python run_bench.py --mode hil --port COM3 --serial MPU-0001 --docs
```

- `--port` : port de l'ESP32 (Windows : `COM3`, `COM4`... ; Linux : `/dev/ttyUSB0`).
- `--serial` : numéro de série que vous donnez au capteur, enregistré dans la traçabilité.
- `--docs` : copie chaque graphique dans le dossier de son TP, sous `images/hil.png`.

Après cette commande, chaque fiche TP peut afficher son graphique réel : il suffit de retirer les marques de commentaire autour de l'image dans la section « Vos résultats sur le vrai capteur ».

## 2. Comparer simulation et réel

```bash
python tools/compare_campaigns.py reports/<campagne_sil> reports/<campagne_hil>
```

L'outil [`tools/compare_campaigns.py`](../../tools/compare_campaigns.py) produit dans `resultats/` :

| Fichier | Contenu |
|---|---|
| `comparaison.md` | Toutes les mesures côte à côte, avec l'écart |
| `compare_T03.png` | Bruit : histogrammes et spectres superposés |
| `compare_T04.png` | Linéarité : écarts à la droite, côte à côte |
| `compare_T07.png` | FFT de l'enveloppe à 10 Hz |
| `compare_T08.png` | Réponse à l'échelon, normalisée |

## 3. Ce à quoi s'attendre

| Test | Écart probable | Explication probable |
|---|---|---|
| TP03 bruit | Bruit plus élevé, pic dans le spectre | Densité de bruit de la datasheet, servo qui frémit en tenant sa position (vers 50 Hz) |
| TP04 linéarité | Écarts plus grands et irréguliers | Erreur de position du servo, de l'ordre du degré |
| TP05 hystérésis | Possible KO | Jeu réel du servo plus grand qu'en simulation |
| TP07 FFT | Pics plus petits, pics parasites | Fixation souple, résonance du bras |
| TP08 échelon | Plus lent, petites oscillations | Servo ralenti par la charge, bras qui vibre à l'arrêt |
| TP10 échantillonnage | Peu d'écart | L'horloge de l'ESP32 est précise |

Un écart n'est pas un échec. Pour chacun, posez-vous la question : **vient-il du capteur ou du banc ?**

## 4. Vos résultats

> **À compléter** après la campagne réelle.

| Test | Simulation | Vrai capteur | Verdict réel | Explication de l'écart |
|---|---|---|---|---|
| TP02 offset max | 45 mg | | | |
| TP03 bruit | 4,0 mg | | | |
| TP04 R² | 0,9999 | | | |
| TP05 hystérésis | 14,4 mg | | | |
| TP07 erreur de fréquence | 0,002 Hz | | | |
| TP08 établissement | 70 ms | | | |
| TP10 fréquence réelle | 500,0 Hz | | | |

Ajoutez ici les graphiques de `resultats/` et, si un seuil a été modifié, la valeur choisie et sa justification.

## Checklist

- [ ] Campagne réelle lancée avec `--docs`
- [ ] Graphiques réels affichés dans chaque fiche TP
- [ ] Comparaison générée et ajoutée ici
- [ ] Chaque écart expliqué
- [ ] Statut des TP mis à jour dans le sommaire

---

[← Module 7 · Matériel et firmware](../07-materiel-et-firmware/README.md) · [Sommaire](../../README.md) · [Module 9 · Carte PCB →](../09-carte-pcb/README.md)
