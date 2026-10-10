# Campagne 20261010-140717_sil_SIM-0001

Mode SIL · capteur SIM-0001 · 2026-10-10 14:07:17

| ID | Test | Verdict | Mesures clés | Critère |
|---|---|---|---|---|
| T01 | Communication I2C | **OK** | WHO_AM_I = 0x68 | WHO_AM_I = 0x68 |
| T02 | Offset et calibration | **OK** | offset brut X (g) = 0.03478; offset brut Y (g) = -0.01989; offset brut Z (g) = 0.04508; résidu X après calibration (g) = 0.0003432 | |offset brut| ≤ 0.15 g et |résidu| ≤ 0.05 g |
| T03 | Bruit au repos | **OK** | écart-type ax (mg) = 3.947; écart-type ay (mg) = 3.947; écart-type az (mg) = 3.984; SNR pour 1 g (dB) = 47.99 | écart-type ≤ 10 mg et SNR ≥ 40 dB |
| T04 | Linéarité | **OK** | R² = 0.9999; erreur max (% PE) = 0.2181; gain mesuré = 1.023; offset mesuré (g) = 0.02774 | R² ≥ 0.99 et erreur ≤ 2.0 % PE |
| T05 | Hystérésis | **OK** | écart max (mg) = 13.92; à l'angle (°) = 0 | écart montée/descente ≤ 20 mg |
| T06 | Répétabilité | **OK** | écart-type (mg) = 0.2038; étendue (mg) = 0.6349 | écart-type sur 10 cycles ≤ 10 mg |
| T07 | Réponse en fréquence (FFT) | **OK** | 5 Hz commandé -> mesuré (Hz) = 5; 10 Hz commandé -> mesuré (Hz) = 10; 20 Hz commandé -> mesuré (Hz) = 20; 40 Hz commandé -> mesuré (Hz) = 40 | pic FFT à ± 1.0 Hz de la fréquence commandée |
| T08 | Temps de réponse | **OK** | temps de montée 10-90 % (ms) = 58.01; temps d'établissement (ms) = 70.02; dépassement (%) = 1.056 | temps d'établissement à 5 % ≤ 500 ms |
| T09 | Validation du filtre passe-bas | **OK** | bruit brut (mg) = 4.036; bruit filtré (mg) = 1.047; réduction du bruit (%) = 74.05; décalage du niveau (%) = 0.001009 | bruit réduit ≥ 50 % et niveau décalé ≤ 1.0 % |
| T10 | Fréquence d'échantillonnage réelle | **OK** | fréquence nominale (Hz) = 500; fréquence mesurée (Hz) = 500; écart (%) = 0.0007004; gigue (%) = 1.069 | écart ≤ 5.0 % et gigue ≤ 5.0 % |
| T12 | Robustesse aux erreurs | **OK** | angle hors plage (200°) = OK : ValueError; acquisition de 0 point = OK : ValueError; commande série inconnue = OK : SensorError; capteur débranché = OK : SensorError | chaque erreur est signalée proprement, sans plantage |
| T13 | Détection de défauts injectés | **OK** | défaut pic = détecté; défaut saturation = détecté; défaut fige = détecté; défaut derive = détecté | 100 % des défauts détectés, 0 fausse alarme |
