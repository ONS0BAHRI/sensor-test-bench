[Formation](../../README.md) › Module 7

# Module 7 · Matériel et firmware

**Statut :** à faire

Ce module construit le banc physique sur breadboard, installe le firmware de l'ESP32 et vérifie chaque commande avant la première campagne réelle.

## 1. Matériel

| Composant | Rôle | Remarque |
|---|---|---|
| ESP32 DevKit | Acquisition à 500 Hz, pilotage du servo et du vibreur | Un Arduino Uno ne suffit pas : pas assez de mémoire pour stocker 4 000 mesures |
| Module GY-521 (MPU6050) | Capteur testé | ±2 g, 16384 LSB/g |
| Servo SG90 (ou MG90S) | Inclinaison à angle connu | Le MG90S a des engrenages métal, avec moins de jeu |
| Mini moteur vibreur 3 V | Vibration à fréquence connue | Moteur à masselotte ou en disque |
| Transistor 2N2222, diode 1N4007, résistance 1 kΩ | Commande du moteur | La diode protège contre les surtensions à la coupure |
| Alimentation 5 V, 2 A | Alimentation du servo | Séparée de l'ESP32 |
| Breadboard, fils, câble USB de données | Câblage | Certains câbles USB ne transportent que le courant |

## 2. Câblage

| Signal | Broche ESP32 | Remarque |
|---|---|---|
| MPU6050 VCC / GND | 3V3 / GND | |
| MPU6050 SDA / SCL | GPIO21 / GPIO22 | I2C à 400 kHz |
| MPU6050 AD0 | GND | Adresse 0x68 |
| Servo signal | GPIO18 | Servo alimenté par le 5 V externe |
| Vibreur | GPIO19 → 1 kΩ → base du 2N2222 | Moteur entre 3V3 et collecteur, émetteur à la masse, diode en parallèle du moteur (cathode côté +) |
| Masses | Toutes reliées | Masse de l'alimentation 5 V reliée à celle de l'ESP32 |

> **À compléter :** schéma de câblage dans `images/cablage.png` (Fritzing, Proteus ou dessin propre photographié).

## 3. Montage mécanique

- Fixez le capteur **sur le bras du servo**, axe X dans le plan de rotation : quand le bras tourne de θ, l'axe X s'incline de θ.
- Le capteur doit être **à plat quand la commande vaut 0°**. Réglez la constante `SERVO_ZERO` du firmware (90 par défaut) jusqu'à lire environ 0 g sur X à 0°.
- Collez le vibreur près du capteur, sur le même support rigide.
- Le câble du capteur doit être souple et ne pas freiner le bras.

> **À compléter :** photo du montage dans `images/montage.jpg`, avec les éléments repérés.

## 4. Installer le firmware

1. Installer l'IDE Arduino.
2. Ajouter le support des cartes ESP32 (gestionnaire de cartes, paquet « esp32 » d'Espressif).
3. Installer la bibliothèque **ESP32Servo** (gestionnaire de bibliothèques).
4. Ouvrir [`firmware/sensor_bench/sensor_bench.ino`](../../firmware/sensor_bench/sensor_bench.ino), choisir la carte « ESP32 Dev Module » et le port, puis téléverser.

Le firmware ne fait qu'exécuter des ordres et renvoyer des mesures horodatées. Toute l'analyse reste en Python. Il stocke une acquisition complète en mémoire avant de l'envoyer : l'écriture sur le port série ne perturbe donc pas la cadence de 500 Hz.

## 5. Le protocole série

| Commande | Réponse |
|---|---|
| `ID?` | `ID 0x68` |
| `FS?` / `VER?` | `FS 500` / `VER 1.0.0` |
| `SERVO 30` | `OK` (angle de −80° à 80°, 0° = à plat) |
| `VIB 10` | `OK` (vibreur modulé à 10 Hz, 0 = arrêt) |
| `READ 1000` | `DATA 1000`, puis 1 000 lignes `t_us,ax,ay,az,gx,gy,gz,temp` en valeurs brutes, puis `END` |
| `STEP 45 1000` | Comme `READ` ; le servo reçoit l'ordre à la mesure 100 |
| Commande invalide | `ERR <message>` |

## 6. Vérifier commande par commande

Ouvrez le moniteur série de l'IDE Arduino à **921600 bauds**, fin de ligne « Nouvelle ligne », puis :

1. `ID?` → `ID 0x68`. Sinon, vérifiez le câblage I2C (TP01).
2. `SERVO 30` puis `SERVO 0` → le bras bouge.
3. `VIB 5` puis `VIB 0` → le moteur pulse puis s'arrête.
4. `READ 5` → 5 lignes de mesures ; la 4e colonne (az) vaut environ 16384 à plat.
5. `FOO` → `ERR commande inconnue: FOO`.

Fermez le moniteur série avant de lancer Python : un port ne peut être ouvert que par un programme à la fois.

## 7. Dépannage

| Symptôme | Cause probable |
|---|---|
| Rien ne s'affiche | Mauvaise vitesse (921600), mauvais câble USB, ou port occupé |
| L'ESP32 redémarre quand le servo bouge | Servo alimenté par l'ESP32 : utilisez l'alimentation 5 V séparée |
| `ERR capteur absent` | SDA et SCL inversés, alimentation du module, masse commune |
| Caractères illisibles | Vitesse du moniteur différente de celle du firmware |

## Vos résultats

> **À compléter :** photo du montage, schéma de câblage, capture du moniteur série avec les cinq commandes.

## Checklist

- [ ] Banc câblé, photo et schéma ajoutés
- [ ] Firmware téléversé
- [ ] Les cinq commandes répondent correctement
- [ ] `SERVO_ZERO` réglé : environ 0 g sur X à 0°

---

[← Module 6 · Automatisation](../06-automatisation/README.md) · [Sommaire](../../README.md) · [Module 8 · Simulation et réel →](../08-simulation-vs-reel/README.md)
