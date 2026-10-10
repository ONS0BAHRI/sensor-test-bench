[Formation](../../README.md) › Module 12

# Module 12 · Démo et présentation

**Statut :** à faire

Un projet n'est convaincant que s'il se montre. Ce module produit les médias du dépôt et une présentation courte, utilisable en entretien ou en soutenance.

## 1. Les médias

| Fichier | Contenu | Conseils |
|---|---|---|
| `media/montage.jpg` | Photo du banc complet | Lumière du jour, fond uni, éléments repérés par des flèches |
| `media/live.gif` | 5 à 10 s d'affichage en direct | `python tools/live_plot.py --mode hil --port COM3`, enregistré avec ScreenToGif (Windows) ou Peek (Linux) |
| Vidéo `.mp4` | Démonstration de 2 à 3 minutes | Sur GitHub, glisser-déposer le fichier dans l'éditeur du README : il est hébergé et affiché directement |

## 2. Scénario de la vidéo

1. Le montage, élément par élément.
2. L'affichage en direct : le servo s'incline, la courbe suit, puis la vibration apparaît.
3. `python run_bench.py --mode hil --port COM3` : les tests défilent, verdict OK.
4. Le rapport HTML : un ou deux graphiques commentés.
5. `python run_bench.py --defective` : le banc rejette un capteur défectueux.

## 3. La présentation

| Diapositive | Contenu |
|---|---|
| 1 | Le problème : comment savoir qu'un capteur est bon ? |
| 2 | Le principe : stimulus connu, mesure, critère, verdict |
| 3 | L'architecture : SIL et HIL, interface commune |
| 4 | Le banc réel (photo) et la carte PCB |
| 5 | Résultats : linéarité, FFT, tableau des verdicts |
| 6 | Simulation et réel : les écarts et leur explication |
| 7 | Automatisation : une commande, un rapport, la traçabilité, la CI |
| 8 | Limites et évolutions (IA, dérive thermique) |

Préparez une réponse pour chaque choix technique : pourquoi 500 Hz, pourquoi ce filtre, pourquoi ce seuil, pourquoi ce servo.

## 4. Décrire le projet en quelques lignes

> **Banc de test automatisé pour capteur inertiel MPU6050**
> - Banc SIL / HIL : ESP32, stimuli contrôlés (servomoteur, vibreur), pilotage en Python.
> - 12 tests automatisés (pytest) : calibration, bruit, linéarité, hystérésis, réponse en fréquence (FFT), temps de réponse, robustesse, détection de défauts. Seuils configurables, traçabilité SQLite, rapports HTML.
> - Intégration continue GitHub Actions, carte PCB dédiée (Proteus), analyses croisées MATLAB.

Adaptez cette description à ce que vous avez réellement réalisé.

## Vos résultats

> **À compléter :** médias dans `media/`, présentation en PDF dans ce dossier, lien de la vidéo.

## Checklist

- [ ] Photo, GIF et vidéo ajoutés
- [ ] Présentation en PDF ajoutée
- [ ] Section « Démo » du README principal à jour

---

[← Module 11 · Intelligence artificielle](../11-intelligence-artificielle/README.md) · [Sommaire](../../README.md)
