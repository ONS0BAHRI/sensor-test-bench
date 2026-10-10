# Journal des modifications

Les changements notables du projet sont consignés ici, du plus récent au plus ancien.

## [Non publié]

### À venir
- Résultats sur le vrai capteur pour chaque TP
- TP11 : dérive thermique
- Module 11 : détection d'anomalies et classification des défauts
- Carte PCB du banc

## [1.0.0]

### Ajouté
- Formation en 12 modules et 13 travaux pratiques, avec résultats de référence en simulation
- Simulateur physique du banc (SIL) et pilote série de l'ESP32 (HIL) avec une interface commune
- 12 procédures de test automatiques et seuils dans `config/limits.yaml`
- Traitement du signal : Butterworth, FFT, enveloppe, régression, réponse indicielle, détection de défauts
- Campagne complète `run_bench.py` : rapport HTML, CSV, traçabilité SQLite, verdict OK / KO
- Firmware ESP32 avec protocole série et acquisition à 500 Hz
- 44 tests pytest, dont un faux ESP32 pour tester le protocole
- Intégration continue GitHub Actions
- Outils : comparaison de campagnes, affichage en direct, étapes pour TestStand, scripts MATLAB
