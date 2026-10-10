# Campagne 20261010-140723_sil_SIM-DEFECT

Mode SIL · capteur SIM-DEFECT · 2026-10-10 14:07:23

| ID | Test | Verdict | Mesures clés | Critère |
|---|---|---|---|---|
| T01 | Communication I2C | **OK** | WHO_AM_I = 0x68 | WHO_AM_I = 0x68 |
| T02 | Offset et calibration | **KO** | offset brut X (g) = 0.2096; offset brut Y (g) = -0.02106; offset brut Z (g) = 0.04544; résidu X après calibration (g) = 0.0006027 | |offset brut| ≤ 0.15 g et |résidu| ≤ 0.05 g |
| T03 | Bruit au repos | **KO** | écart-type ax (mg) = 13.04; écart-type ay (mg) = 13.18; écart-type az (mg) = 13.01; SNR pour 1 g (dB) = 37.6 | écart-type ≤ 10 mg et SNR ≥ 40 dB |
| T04 | Linéarité | **OK** | R² = 0.9998; erreur max (% PE) = 0.2895; gain mesuré = 1.034; offset mesuré (g) = 0.1803 | R² ≥ 0.99 et erreur ≤ 2.0 % PE |
| T05 | Hystérésis | **KO** | écart max (mg) = 57.59; à l'angle (°) = 0 | écart montée/descente ≤ 20 mg |
| T06 | Répétabilité | **OK** | écart-type (mg) = 0.6695; étendue (mg) = 2.066 | écart-type sur 10 cycles ≤ 10 mg |
| T07 | Réponse en fréquence (FFT) | **OK** | 5 Hz commandé -> mesuré (Hz) = 5.001; 10 Hz commandé -> mesuré (Hz) = 9.996; 20 Hz commandé -> mesuré (Hz) = 20; 40 Hz commandé -> mesuré (Hz) = 40 | pic FFT à ± 1.0 Hz de la fréquence commandée |
| T08 | Temps de réponse | **OK** | temps de montée 10-90 % (ms) = 54; temps d'établissement (ms) = 65.99; dépassement (%) = 1.246 | temps d'établissement à 5 % ≤ 500 ms |
| T09 | Validation du filtre passe-bas | **OK** | bruit brut (mg) = 12.79; bruit filtré (mg) = 3.103; réduction du bruit (%) = 75.74; décalage du niveau (%) = 0.002898 | bruit réduit ≥ 50 % et niveau décalé ≤ 1.0 % |
| T10 | Fréquence d'échantillonnage réelle | **OK** | fréquence nominale (Hz) = 500; fréquence mesurée (Hz) = 500; écart (%) = 0.0006253; gigue (%) = 1.007 | écart ≤ 5.0 % et gigue ≤ 5.0 % |
| T12 | Robustesse aux erreurs | **OK** | angle hors plage (200°) = OK : ValueError; acquisition de 0 point = OK : ValueError; commande série inconnue = OK : SensorError; capteur débranché = OK : SensorError | chaque erreur est signalée proprement, sans plantage |
| T13 | Détection de défauts injectés | **OK** | défaut pic = détecté; défaut saturation = détecté; défaut fige = détecté; défaut derive = détecté | 100 % des défauts détectés, 0 fausse alarme |
