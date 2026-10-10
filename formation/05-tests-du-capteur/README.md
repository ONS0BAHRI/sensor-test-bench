[Formation](../../README.md) › Module 5

# Module 5 · Tests du capteur

Ce module est le cœur de la formation : 13 travaux pratiques, chacun consacré à une caractéristique du capteur. Chaque TP se fait d'abord en simulation, puis sur le vrai capteur, avec la même procédure automatique.

## Les travaux pratiques

| TP | Caractéristique | Question à laquelle il répond |
|---|---|---|
| [TP01](TP01-communication-i2c/README.md) | Communication I2C | Le capteur répond-il ? |
| [TP02](TP02-offset-et-calibration/README.md) | Offset et calibration | Que mesure-t-il quand la grandeur vaut zéro ? |
| [TP03](TP03-bruit/README.md) | Bruit au repos | Quelle est la plus petite variation mesurable ? |
| [TP04](TP04-linearite/README.md) | Linéarité | La sortie est-elle proportionnelle à l'entrée ? |
| [TP05](TP05-hysteresis/README.md) | Hystérésis | La mesure dépend-elle du sens d'arrivée ? |
| [TP06](TP06-repetabilite/README.md) | Répétabilité | La même consigne donne-t-elle la même mesure ? |
| [TP07](TP07-reponse-en-frequence/README.md) | Réponse en fréquence | Une vibration est-elle restituée à la bonne fréquence ? |
| [TP08](TP08-temps-de-reponse/README.md) | Temps de réponse | À quelle vitesse la mesure suit-elle un changement ? |
| [TP09](TP09-filtre-numerique/README.md) | Filtre numérique | Le filtre retire-t-il le bruit sans fausser la mesure ? |
| [TP10](TP10-echantillonnage/README.md) | Échantillonnage | La cadence réelle est-elle celle annoncée ? |
| [TP11](TP11-derive-thermique/README.md) | Dérive thermique | Le zéro change-t-il avec la température ? |
| [TP12](TP12-robustesse/README.md) | Robustesse | Le banc gère-t-il les pannes sans planter ? |
| [TP13](TP13-detection-de-defauts/README.md) | Détection de défauts | Les défauts typiques sont-ils repérés ? |

L'ordre est conseillé : TP01 valide la communication, TP02 à TP06 caractérisent le capteur en statique, TP07 à TP10 en dynamique et en traitement du signal, TP12 et TP13 valident le banc lui-même. TP11 est un exercice de conception : la procédure est à écrire.

## Organisation d'une fiche TP

Chaque dossier contient un `README.md` et un dossier `images/`. La fiche suit toujours le même plan :

| Section | Contenu |
|---|---|
| 1 à 4 | Pourquoi ce test, notions, conditions de mesure, méthode |
| 5 et 6 | Le code de la procédure et le critère d'acceptation (extrait de `limits.yaml`) |
| 7 | Les commandes pour lancer le TP en simulation et sur le vrai capteur |
| 8 | Le résultat de référence obtenu en simulation, avec son graphique (`images/sil.png`) |
| 9 | Ce qui serait anormal |
| 10 | **Vos résultats sur le vrai capteur** : tableau, graphique (`images/hil.png`) et analyse à compléter |
| 11 et 12 | Pour aller plus loin, questions de révision avec réponses |
| Checklist | Les étapes pour considérer le TP comme terminé |

## Ranger automatiquement les graphiques

```bash
python run_bench.py --docs                              # images/sil.png dans chaque TP
python run_bench.py --mode hil --port COM3 --docs       # images/hil.png dans chaque TP
python run_bench.py --defective --docs                  # images/defectueux.png
```

## Ajouter un nouveau TP

Copiez [`_modele-tp.md`](_modele-tp.md) dans un nouveau dossier `TPxx-nom/`, écrivez la procédure dans `bench/procedures.py`, ses seuils dans `config/limits.yaml`, son graphique dans `report/plots.py`, puis déclarez le dossier dans `report/course.py`.

---

[← Module 4 · Traitement du signal](../04-traitement-du-signal/README.md) · [Sommaire](../../README.md) · [TP01 →](TP01-communication-i2c/README.md)
