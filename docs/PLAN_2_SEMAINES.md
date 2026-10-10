# Plan accéléré : 2 semaines jusqu'à l'envoi du CV

La version 1 du code est prête et testée en simulation. Les deux semaines servent à **comprendre chaque ligne**, passer sur le **vrai matériel** et produire les **preuves** (photos, vidéo, résultats réels).

## Semaine 1 : comprendre et mettre en ligne

| Jour | À faire | Résultat attendu |
|---|---|---|
| J1 | Installer Python, lancer `pytest` et `python run_bench.py`, ouvrir le rapport HTML | 44 tests verts sur ton PC |
| J1 | Créer le dépôt GitHub, remplacer `TON-PSEUDO` dans le README, pousser le code | CI verte sur GitHub |
| J2 | Lire `bench/base.py` et `bench/simulated_sensor.py`. Changer un paramètre (bruit 0,012) et voir T03 passer KO | Tu sais expliquer SIL / HIL |
| J3 | Lire `processing/signal_tools.py` et ses tests : FFT, Butterworth, enveloppe, régression | Tu sais expliquer chaque fonction |
| J4 | Lire `bench/procedures.py` test par test, avec la section 7 du README | Tu sais présenter chaque TP |
| J5 | Câbler le banc (section 5), téléverser le firmware, tester `ID?`, `SERVO 30`, `READ 10` au moniteur série | Le matériel répond |
| J6-J7 | Fixer le capteur sur le servo, première campagne `--mode hil`, ajuster `SERVO_ZERO` et les seuils si besoin | Premier rapport réel |

## Semaine 2 : résultats réels et présentation

| Jour | À faire | Résultat attendu |
|---|---|---|
| J8 | Campagne HIL complète avec `--docs`, remplir le tableau 7.13 du README | Résultats réels publiés |
| J9 | Photos du montage, schéma de câblage, GIF de `tools/live_plot.py` | Section Démo remplie |
| J10 | Vidéo de 2 à 3 minutes (montage, live, verdict OK puis capteur défectueux KO) | Vidéo dans le README |
| J11 | Ajouter le projet au CV et sur LinkedIn | CV prêt |
| J12 | Préparer 8 diapositives et répéter l'explication en 5 minutes | Prêt pour l'entretien |
| J13-J14 | Marge, puis début de la V2 (IA) | CV envoyé |

## Si tu manques de temps

Le minimum pour envoyer le CV : dépôt en ligne avec CI verte, README avec les résultats SIL, **une photo du montage** et **une campagne HIL**, même partielle. La V2 (IA, tableau de bord) peut arriver après l'envoi : un dépôt qui continue d'évoluer est un bon signal.
