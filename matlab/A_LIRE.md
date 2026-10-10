# Analyse des données du banc en MATLAB

Ces scripts refont trois TP (T03 bruit, T04 linéarité, T07 FFT) en MATLAB, à partir des mêmes fichiers CSV que le code Python. Objectif : découvrir MATLAB avec tes propres données, et vérifier que deux outils différents donnent les mêmes résultats.

## Utilisation

1. Lancer une campagne en Python : `python run_bench.py` (ou `--mode hil` avec le vrai capteur).
2. Ouvrir MATLAB Online (gratuit, 20 h par mois avec un compte MathWorks) ou GNU Octave (gratuit, installé sur le PC).
3. Envoyer le dossier `matlab/` et le dossier `reports/<campagne>/raw/` dans MATLAB Drive, en gardant la même organisation.
4. Dans chaque script, remplacer `METTRE_ICI_LE_NOM_DE_LA_CAMPAGNE` par le nom du dossier de la campagne.
5. Se placer dans le dossier `matlab/` et lancer `tp_bruit`, `tp_linearite` puis `tp_fft`.

## Exercices

- Comparer les valeurs affichées avec le rapport HTML Python : elles doivent être identiques à l'arrondi près (sauf T07, où l'enveloppe est calculée autrement).
- Dans `tp_fft.m`, remplacer la moyenne glissante par `butter` + `filtfilt` (Signal Processing Toolbox, incluse dans MATLAB Online gratuit).
- Écrire `tp_echelon.m` pour T08 en t'inspirant de `processing/signal_tools.py` (fonction `step_response`).

Ces scripts n'utilisent que des fonctions de base (`dlmread`, `fft`, `polyfit`, `conv`, `hist`) pour fonctionner aussi sous Octave.
