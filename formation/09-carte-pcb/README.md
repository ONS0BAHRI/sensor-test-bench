[Formation](../../README.md) › Module 9

# Module 9 · Carte PCB du banc

**Statut :** à faire

La breadboard suffit pour démarrer, mais elle ajoute des faux contacts et du bruit. Ce module spécifie une carte d'accueil pour l'ESP32 DevKit, à concevoir avec Proteus (ou KiCad). **Elle utilise les mêmes broches que le firmware : aucune ligne de code à changer.**

Le MPU6050 reste sur le bras du servo : la carte lui fournit un connecteur et un câble court.

## 1. Alimentation : trois règles

1. **L'ESP32 est alimenté par son USB**, qui sert aussi aux données. Ne reliez pas le 5 V externe à la broche 5V/VIN du DevKit tant que l'USB est branché : selon les cartes, le courant peut refluer vers le PC.
2. **Le servo est alimenté par le 5 V externe** (bloc secteur 5 V, 2 A) : il consomme plusieurs centaines de mA, davantage en blocage.
3. **Le vibreur a son propre régulateur 3,3 V**, alimenté par le 5 V externe : ses pointes de courant ne perturbent pas le 3,3 V du capteur.

Toutes les masses sont communes et se rejoignent en un point, près du connecteur d'alimentation (masse en étoile).

## 2. Nomenclature

| Réf. | Composant | Valeur / boîtier | Rôle |
|---|---|---|---|
| U1 | ESP32 DevKit | Barrettes femelles 2 × 15 ou 2 × 19 | Microcontrôleur. Mesurez l'entraxe des rangées de votre carte : il varie selon les modèles |
| U2 | AMS1117-3.3 | SOT-223 | 3,3 V dédié au vibreur |
| J1 | Jack DC 5,5 × 2,1 mm | Traversant | Entrée 5 V externe |
| F1 | Fusible réarmable | 1,5 A | Protection contre un court-circuit |
| D2 | Diode Schottky SS34 | SMA | Protection contre l'inversion de polarité |
| C1 | Condensateur électrolytique | 470 µF, 10 V | Réserve pour les appels de courant du servo |
| C2, C3 | Condensateurs céramique | 100 nF | Découplage du 5 V et du 3,3 V vibreur |
| C4, C5 | Condensateurs | 10 µF | Entrée et sortie de U2 |
| J3 | Connecteur capteur | JST-XH 5 broches | 3V3, GND, SDA, SCL, INT |
| J4 | Second connecteur capteur (option) | JST-XH 5 broches | Deuxième MPU6050 avec AD0 à 3,3 V (adresse 0x69) |
| J5 | Connecteur servo | Barrette mâle 3 broches | GND, +5 V, signal (ordre standard des servos) |
| J6 | Connecteur vibreur | JST-XH 2 broches | Moteur |
| Q1 | NPN 2N2222 (ou MOSFET AO3400) | TO-92 ou SOT-23 | Commande du moteur |
| R1 | Résistance | 1 kΩ | Base de Q1 |
| D1 | Diode 1N4148 ou 1N4007 | | Roue libre aux bornes du moteur |
| C6 | Condensateur céramique | 100 nF | Antiparasite aux bornes du moteur |
| R2, R3 | Résistances de tirage I2C | 4,7 kΩ, non montées par défaut | Le GY-521 a déjà les siennes : emplacement prévu au cas où |
| LED1, R4 | LED et résistance | 1 kΩ | Présence du 5 V externe |
| TP1 à TP8 | Points de test | Boucles ou pastilles | Oscilloscope, analyseur logique |
| H1 à H4 | Trous de fixation | M3 | |

## 3. Liste des connexions

| Net | Relie |
|---|---|
| 5V_EXT | J1 (+) → F1 → D2 → C1, C2, J5 (+5 V), entrée de U2, LED1 |
| 3V3_ESP | U1 3V3 → J3 et J4 (3V3), R2 et R3 si montées |
| 3V3_VIB | Sortie de U2 → J6 (+ moteur), cathode de D1, C3 |
| GND | J1 (−), U1 GND, U2, J3, J4, J5, émetteur de Q1, condensateurs |
| SDA | U1 GPIO21 → J3, J4 |
| SCL | U1 GPIO22 → J3, J4 |
| MPU_INT | U1 GPIO4 → J3 (INT), réservé pour une évolution du firmware |
| SERVO_PWM | U1 GPIO18 → J5 (signal) |
| VIB_CMD | U1 GPIO19 → R1 → base de Q1 |
| VIB_OUT | Collecteur de Q1 → J6 (− moteur), anode de D1, C6 |

## 4. Points de test

Prévoir des points de mesure dès la conception s'appelle la **conception pour le test** (*Design for Test*).

| Point | Net | Pourquoi |
|---|---|---|
| TP1 | GND | Masse de la sonde |
| TP2 | 3V3_ESP | Alimentation du capteur |
| TP3 | 5V_EXT | Chutes de tension au démarrage du servo |
| TP4, TP5 | SDA, SCL | Décodage des trames I2C |
| TP6 | SERVO_PWM | Impulsions de 500 à 2 400 µs toutes les 20 ms |
| TP7 | VIB_CMD | Fréquence de modulation du vibreur |
| TP8 | VIB_OUT | Effet de la diode de roue libre |

## 5. Règles de routage

- Pistes 5V_EXT, servo et moteur : 1 mm minimum. Signaux : 0,3 mm.
- Plan de masse sur la face inférieure, sans le couper sous les lignes I2C.
- SDA et SCL courtes, loin des pistes du moteur et du servo. Câble vers le capteur de moins de 30 cm, chaque signal torsadé avec une masse.
- C1 au plus près de J5 ; C3 et C6 au plus près de J6.
- Sérigraphie : nom de chaque connecteur et point de test, ordre des broches, nom et version de la carte.

## 6. Validation de la carte reçue

1. **Avant de placer l'ESP32 :** continuité des masses, absence de court-circuit entre 5V_EXT et GND.
2. Alimentation seule : 5 V sur TP3, 3,3 V en sortie de U2, LED allumée.
3. ESP32 en place : `ID?` au moniteur série, puis les commandes du module 7.
4. Campagne complète, puis comparaison avec la campagne sur breadboard :

```bash
python tools/compare_campaigns.py reports/<campagne_breadboard> reports/<campagne_pcb> --labels "Breadboard" "PCB" --out formation/09-carte-pcb/resultats
```

Le bruit (TP03) est l'indicateur le plus parlant : une bonne carte doit faire au moins aussi bien que la breadboard.

## Vos résultats

> **À compléter :**
> - `schema/` : schéma Proteus en PDF et fichier source.
> - `images/` : capture du routage, vue 3D, photo de la carte assemblée.
> - `fabrication/` : fichiers Gerber et de perçage envoyés au fabricant.
> - `resultats/` : comparaison breadboard / PCB.

## Checklist

- [ ] Schéma conforme à la liste des connexions
- [ ] Routage, vue 3D et Gerber ajoutés
- [ ] Carte validée électriquement (section 6)
- [ ] Campagne sur PCB et comparaison avec la breadboard

---

[← Module 8 · Simulation et réel](../08-simulation-vs-reel/README.md) · [Sommaire](../../README.md) · [Module 10 · Outils industriels →](../10-outils-industriels/README.md)
