# Médias à ajouter

Fichiers attendus par le README :

| Fichier | Contenu | Conseil |
|---|---|---|
| `montage.jpg` | photo du banc complet | lumière du jour, fond uni, flèches vers ESP32, capteur, servo, vibreur |
| `cablage.png` | schéma de câblage | Fritzing (gratuit) ou dessin propre photographié |
| `live.gif` | 5 à 10 s de `tools/live_plot.py` | ScreenToGif (Windows) ou Peek (Linux), moins de 10 Mo |
| vidéo `.mp4` | démo de 2 à 3 minutes | glisser-déposer directement dans le README sur GitHub (limite 10 Mo en gratuit) |

Scénario de vidéo :
1. Présentation du montage (15 s).
2. `python tools/live_plot.py --mode hil --port COM3` : le servo s'incline, la courbe suit, puis la vibration apparaît (30 s).
3. `python run_bench.py --mode hil --port COM3` : les tests défilent, verdict OK (45 s).
4. Ouverture du rapport HTML : un ou deux graphiques commentés (30 s).
5. `python run_bench.py --defective` : le banc rejette le capteur défectueux (20 s).
