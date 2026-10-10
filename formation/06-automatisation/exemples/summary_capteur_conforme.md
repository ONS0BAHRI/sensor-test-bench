# Campagne 20261010-125743_sil_SIM-0001

Mode SIL · capteur SIM-0001 · 2026-10-10 12:57:43

| ID | Test | Verdict | Mesures clés | Critère |
|---|---|---|---|---|
| T01 | Communication I2C | **OK** | WHO_AM_I = 0x68 | WHO_AM_I = 0x68 |
| T02 | Offset et calibration | **OK** | offset brut X (g) = 0.03488; offset brut Y (g) = -0.02033; offset brut Z (g) = 0.04514; résidu X après calibration (g) = 0.0001851 | |offset brut| ≤ 0.15 g et |résidu| ≤ 0.05 g |
| T03 | Bruit au repos | **OK** | écart-type ax (mg) = 4.011; écart-type ay (mg) = 4.056; écart-type az (mg) = 4.005; SNR pour 1 g (dB) = 47.84 | écart-type ≤ 10 mg et SNR ≥ 40 dB |
| T04 | Linéarité | **OK** | R² = 0.9999; erreur max (% PE) = 0.2211; gain mesuré = 1.023; offset mesuré (g) = 0.0279 | R² ≥ 0.99 et erreur ≤ 2.0 % PE |
| T05 | Hystérésis | **OK** | écart max (mg) = 14.43; à l'angle (°) = 0 | écart montée/descente ≤ 20 mg |
| T06 | Répétabilité | **OK** | écart-type (mg) = 0.2067; étendue (mg) = 0.6368 | écart-type sur 10 cycles ≤ 10 mg |
| T07 | Réponse en fréquence (FFT) | **OK** | 5 Hz commandé -> mesuré (Hz) = 5; 10 Hz commandé -> mesuré (Hz) = 9.999; 20 Hz commandé -> mesuré (Hz) = 20; 40 Hz commandé -> mesuré (Hz) = 40 | pic FFT à ± 1.0 Hz de la fréquence commandée |
| T08 | Temps de réponse | **OK** | temps de montée 10-90 % (ms) = 57.96; temps d'établissement (ms) = 69.98; dépassement (%) = 0.9491 | temps d'établissement à 5 % ≤ 500 ms |
| T09 | Validation du filtre passe-bas | **OK** | bruit brut (mg) = 3.936; bruit filtré (mg) = 0.9552; réduction du bruit (%) = 75.73; décalage du niveau (%) = 0.001202 | bruit réduit ≥ 50 % et niveau décalé ≤ 1.0 % |
| T10 | Fréquence d'échantillonnage réelle | **OK** | fréquence nominale (Hz) = 500; fréquence mesurée (Hz) = 500; écart (%) = 0.0006253; gigue (%) = 1.007 | écart ≤ 5.0 % et gigue ≤ 5.0 % |
| T12 | Robustesse aux erreurs | **OK** | angle hors plage (200°) = OK : ValueError; acquisition de 0 point = OK : ValueError; commande série inconnue = OK : SensorError; capteur débranché = OK : SensorError | chaque erreur est signalée proprement, sans plantage |
| T13 | Détection de défauts injectés | **OK** | défaut pic = détecté; défaut saturation = détecté; défaut fige = détecté; défaut derive = détecté | 100 % des défauts détectés, 0 fausse alarme |
