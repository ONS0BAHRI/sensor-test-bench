[Formation](../../README.md) › Module 10

# Module 10 · Outils industriels : MATLAB, LabVIEW, TestStand

**Statut :** à faire

Les bancs de test industriels utilisent souvent MATLAB, LabVIEW et TestStand. Ce module refait une partie du projet avec chacun de ces outils, pour comprendre leur rôle et les comparer à ce que vous avez construit en Python.

## 1. Accès

| Outil | Rôle en test | Accès gratuit ou d'essai (vérifié en octobre 2026) |
|---|---|---|
| [MATLAB](https://au.mathworks.com/products/matlab-online/matlab-online-versions.html) | Calcul, traitement du signal, Simulink | MATLAB Online : 20 heures par mois, avec la Signal Processing Toolbox |
| GNU Octave | Équivalent libre de MATLAB | Gratuit et illimité |
| [LabVIEW](https://www.ni.com/en/shop/labview/select-edition/labview-community-edition.html) | Programmation graphique de bancs de mesure, pilotage d'instruments | Community Edition gratuite pour un usage personnel non commercial |
| [TestStand](https://www.ni.com/ja/shop/electronic-test-instrumentation/application-software-for-electronic-test-and-instrumentation-category/what-is-teststand/free-trial) | Séquenceur de tests : ordre, limites, rapports, base de données | Essai de 7 jours, prolongeable de 45 jours depuis le logiciel |

Les conditions peuvent évoluer : vérifiez-les sur le site de l'éditeur. La période d'essai de TestStand démarre à l'activation : installez-le seulement quand vous pouvez vous y consacrer.

## 2. MATLAB : refaire trois TP avec vos données

Le dossier [`matlab/`](../../matlab/A_LIRE.md) contient trois scripts qui lisent les mêmes CSV que Python :

| Script | TP | Ce qu'il calcule |
|---|---|---|
| `tp_bruit.m` | TP03 | Écart-type par axe, SNR, histogramme, spectre avec fenêtre de Hann |
| `tp_linearite.m` | TP04 | Régression `polyfit`, gain, offset, R², erreur en % PE |
| `tp_fft.m` | TP07 | Enveloppe, FFT, fréquence du pic |

Ils n'utilisent que des fonctions de base, compatibles avec GNU Octave. Objectif : retrouver **les mêmes valeurs** qu'en Python, ce qui valide le traitement du signal par un second outil.

Exercices :

1. Lancer les trois scripts sur une campagne en simulation, puis sur une campagne réelle.
2. Dans `tp_fft.m`, remplacer la moyenne glissante par `butter` et `filtfilt` (ordre 4, coupure 60 Hz).
3. Écrire `tp_echelon.m` pour le TP08.

## 3. LabVIEW : deux VI à construire

**VI 1 · Lire une campagne et faire la FFT** (sans matériel)

1. *Read Delimited Spreadsheet* : ouvrir `T03_repos.csv`, séparateur virgule, sauter la première ligne.
2. *Index Array* : extraire la colonne 3 (az).
3. *Build Waveform* avec dt = 0,002 s (500 Hz), affichage dans un *Waveform Graph*.
4. *Std Deviation and Variance* : comparer l'écart-type au rapport Python.
5. Express VI *Spectral Measurements* : spectre d'amplitude, fenêtre de Hann.

**VI 2 · Piloter le vrai banc** (ESP32 et pilote NI-VISA)

1. *VISA Configure Serial Port* : port de l'ESP32, 921600 bauds, caractère de fin `\n` activé.
2. *VISA Write* `ID?\n`, puis *VISA Read* : afficher `ID 0x68`.
3. Boucle *While* avec un curseur d'angle : à chaque changement, envoyer `SERVO <angle>\n`.

Le VI 2 montre un point fort de l'architecture : **le firmware ne dépend pas de l'outil côté PC**. Python, LabVIEW et TestStand parlent le même protocole.

## 4. TestStand : comparer avec le séquenceur Python

`run_bench.py` est un petit séquenceur : il enchaîne les tests, applique les limites et produit un rapport. TestStand fait la même chose de façon standardisée. Le fichier [`tools/teststand_steps.py`](../../tools/teststand_steps.py) expose des fonctions de mesure simples :

| Fonction | Renvoie | Limite à saisir dans TestStand |
|---|---|---|
| `ouvrir_banc("sil")` ou `ouvrir_banc("hil", "COM3")` | Description du banc | Étape *Action* |
| `who_am_i()` | 104 (0x68) | Égal à 104 |
| `bruit_mg()` | Bruit en mg | Haute : 10 |
| `r2_linearite()` | R² | Basse : 0,99 |
| `hysteresis_mg()` | Hystérésis en mg | Haute : 20 |
| `erreur_frequence_hz()` | Erreur en Hz | Haute : 1 |
| `temps_etablissement_ms()` | Temps en ms | Haute : 500 |
| `fermer_banc()` | | Étape *Action* finale |

Créez une séquence avec l'adaptateur Python, une étape *Numeric Limit Test* par fonction, lancez-la et ouvrez le rapport généré par TestStand. Vérifiez d'abord les fonctions sans TestStand : `python tools/teststand_steps.py`.

## Vos résultats

> **À compléter :** dans `images/`, captures des figures MATLAB, des deux VI LabVIEW (face avant et diagramme) et de la séquence TestStand avec son rapport. Notez ici les valeurs obtenues et leur comparaison avec Python.

| Outil | Mesure | Python | Outil | Identique ? |
|---|---|---|---|---|
| MATLAB | Bruit Z (mg) | | | |
| MATLAB | R² | | | |
| LabVIEW | Bruit Z (mg) | | | |
| TestStand | Verdict de la séquence | | | |

## Checklist

- [ ] Scripts MATLAB lancés, valeurs identiques à Python
- [ ] VI 1 et VI 2 LabVIEW construits
- [ ] Séquence TestStand exécutée
- [ ] Captures ajoutées

---

[← Module 9 · Carte PCB](../09-carte-pcb/README.md) · [Sommaire](../../README.md) · [Module 11 · Intelligence artificielle →](../11-intelligence-artificielle/README.md)
