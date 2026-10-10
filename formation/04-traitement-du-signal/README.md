[Formation](../../README.md) › Module 4

# Module 4 · Traitement du signal

**Statut :** à faire

Tous les indicateurs du banc sont calculés par une petite boîte à outils : [`processing/signal_tools.py`](../../processing/signal_tools.py). Chaque fonction est courte, documentée et vérifiée par un test unitaire sur un signal dont on connaît la réponse exacte.

## 1. Les outils

| Fonction | Ce qu'elle fait | Utilisée dans |
|---|---|---|
| `moving_average(x, width)` | Moyenne glissante | Comparaison avec le filtre |
| `butter_lowpass(x, fs, fc, order)` | Filtre passe-bas Butterworth, appliqué en aller-retour (phase nulle) | TP08, TP09 |
| `envelope(x, fs, fc)` | Redressement puis passe-bas : révèle une modulation lente | TP07 |
| `spectrum(x, fs)` | Spectre d'amplitude avec fenêtre de Hann | TP03, TP07 |
| `dominant_frequency(x, fs, fmin, fmax)` | Pic principal, affiné par interpolation parabolique | TP07 |
| `snr_db(niveau, bruit)` | Rapport signal sur bruit en dB | TP03 |
| `linear_fit(attendu, mesuré)` | Régression : gain, offset, R², écart maximal | TP04 |
| `step_response(t, x, t_step, tol)` | Temps de montée, d'établissement, dépassement | TP08 |
| `effective_sample_rate(t_us)` | Fréquence réelle et gigue | TP10 |
| `detect_faults(x, fs, ...)` | Cinq règles de détection de défauts | TP13 |
| `inject_fault(x, défaut, fs)` | Injection d'un défaut connu | TP13 |

## 2. Trois idées à retenir

**Filtrer sans retarder.** Un filtre normal retarde le signal. `butter_lowpass` utilise `sosfiltfilt` : le signal est filtré dans un sens puis dans l'autre, ce qui annule le retard. C'est indispensable pour mesurer un temps de réponse (TP08), mais impossible en temps réel.

**Fenêtrer avant la FFT.** Une acquisition coupe le signal brutalement à ses deux extrémités, ce qui étale l'énergie d'une fréquence sur ses voisines (fuite spectrale). La fenêtre de Hann adoucit ces bords.

**Choisir des statistiques robustes.** Pour détecter un pic, la médiane et le MAD (écart absolu médian) ne sont presque pas influencés par le pic lui-même, contrairement à la moyenne et à l'écart-type.

## 3. Tester les outils eux-mêmes

Un outil de mesure doit être validé avant de servir à mesurer. Les tests de [`tests/test_signal_tools.py`](../../tests/test_signal_tools.py) utilisent des signaux à réponse connue :

| Test | Signal d'entrée | Résultat attendu |
|---|---|---|
| Fréquence dominante | Sinus à 12,3 Hz | 12,3 Hz à 0,05 Hz près |
| Amplitude du spectre | Sinus de 0,2 g à 25 Hz | 0,2 g à 5 % près |
| Filtre passe-bas | 2 Hz + 150 Hz, coupure 20 Hz | Il ne reste que le 2 Hz |
| Enveloppe | Porteuse à 170 Hz modulée à 8 Hz | Pic à 8 Hz |
| Régression | Droite 1,03·x + 0,02 | Gain 1,03, offset 0,02, R² = 1 |
| Réponse indicielle | Système du 1er ordre, τ = 50 ms | Établissement à 5 % ≈ 3τ, montée ≈ 2,2τ |
| Détection de défauts | Signal sain, puis 5 défauts injectés | Aucune fausse alarme, 5 défauts détectés |

```bash
pytest tests/test_signal_tools.py -v
```

## 4. Exercices

1. Dans un terminal Python, générez un sinus de 7 Hz échantillonné à 500 Hz et retrouvez sa fréquence avec `dominant_frequency`.
2. Filtrez un signal bruité avec `butter_lowpass` à 5, 20 et 50 Hz, et mesurez l'écart-type restant. Comparez à la règle √(250 / fc).
3. Écrivez un test unitaire pour `moving_average` : la moyenne glissante d'un signal constant doit rester constante (en dehors des bords).

## Vos résultats

> **À compléter :** collez vos scripts d'exercice dans `exercices/` et notez ici les valeurs obtenues.

## Checklist

- [ ] Je sais expliquer le filtrage aller-retour, la fenêtre de Hann et le MAD
- [ ] Les tests unitaires passent
- [ ] Les trois exercices sont faits

---

[← Module 3 · Simulateur](../03-simulateur/README.md) · [Sommaire](../../README.md) · [Module 5 · Tests du capteur →](../05-tests-du-capteur/README.md)
