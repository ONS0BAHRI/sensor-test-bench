[Formation](../../../README.md) › [5 · Tests du capteur](../README.md) › TP07

# TP07 · Réponse en fréquence (FFT)

**Statut :** à faire

| | |
|---|---|
| **Objectif** | Vérifier que le capteur et la chaîne d'acquisition restituent une vibration à la bonne fréquence. |
| **Procédure** | `t07_frequence` dans [`bench/procedures.py`](../../../bench/procedures.py) |
| **Seuils** | section `T07_frequence` de [`config/limits.yaml`](../../../config/limits.yaml) |
| **Modes** | simulation (SIL) et vrai capteur (HIL) |

## 1. Pourquoi ce test

Un capteur utilisé pour surveiller des vibrations (moteurs, machines) doit restituer la bonne fréquence. La FFT est l'outil de base de tout traitement du signal.

## 2. Notions à connaître

- FFT (transformée de Fourier rapide) : décompose un signal en fréquences.
- Résolution fréquentielle = fe / N : 500 Hz / 2 000 points = 0,25 Hz.
- Enveloppe : redressement puis filtrage passe-bas ; elle révèle une modulation lente sur une porteuse rapide.
- Shannon-Nyquist : on ne peut mesurer que les fréquences inférieures à fe / 2 = 250 Hz.
- Un signal carré contient des harmoniques impaires : 3f, 5f, etc.

## 3. Conditions de mesure

Vibreur allumé et éteint (modulation tout-ou-rien) à 5, 10, 20 et 40 Hz. 2 000 mesures par fréquence.

## 4. Méthode

1. Pour chaque fréquence : commander le vibreur, attendre 0,5 s, acquérir 2 000 mesures sur Z.
2. Calculer l'enveloppe : |signal − moyenne| filtré passe-bas à 60 Hz.
3. FFT de l'enveloppe avec fenêtre de Hann, recherche du pic entre 1 et 60 Hz, affiné par interpolation parabolique.
4. Comparer la fréquence trouvée à la fréquence commandée.

## 5. Le code

La procédure pilote le banc, calcule les indicateurs et compare aux seuils. Elle est identique en simulation et sur le vrai capteur.

<details>
<summary>Voir le code de <code>t07_frequence</code></summary>

```python
def t07_frequence(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T07_frequence"]
    fs = bench.sample_rate
    bench.set_angle(0)
    bench.wait(lim["acquisition"]["settle_s"])
    found, spectra, raws = {}, {}, {}
    try:
        for f in c["frequencies_hz"]:
            bench.set_vibration(f)
            bench.wait(0.5)
            m = bench.read(c["n"])
            env = sp.envelope(m.az, fs, c["envelope_fc_hz"])
            found[f] = sp.dominant_frequency(env, fs, fmin=1.0, fmax=c["envelope_fc_hz"])
            spectra[f] = sp.spectrum(env, fs)
            raws[f"vibration_{f}Hz"] = m
            if f == c["frequencies_hz"][1]:
                raw_example = (m.t, m.az, env)
    finally:
        bench.set_vibration(0)
    errors = {f: abs(found[f] - f) for f in found}
    worst = max(errors.values())
    measures = {f"{f} Hz commandé -> mesuré (Hz)": found[f] for f in found}
    measures["erreur max (Hz)"] = worst
    return TestResult("T07", "Réponse en fréquence (FFT)", worst <= c["max_error_hz"],
                      f"pic FFT à ± {c['max_error_hz']} Hz de la fréquence commandée",
                      measures, {"spectra": spectra, "found": found, "example": raw_example}, raws)
```

</details>

## 6. Critère d'acceptation

Extrait de `config/limits.yaml` :

```yaml
T07_frequence:
  frequencies_hz:
  - 5
  - 10
  - 20
  - 40
  n: 2000
  envelope_fc_hz: 60
  max_error_hz: 1.0
```

Critère vérifié : **pic FFT à ± 1.0 Hz de la fréquence commandée**.

## 7. Lancer le TP

```bash
pytest tests/test_bench.py -k t07 -s                         # simulation
pytest tests/test_bench.py -k t07 -s --mode hil --port COM3  # vrai capteur (Linux : /dev/ttyUSB0)
python run_bench.py --mode hil --port COM3 --docs              # campagne complète, graphiques rangés dans les TP
```

## 8. Résultat de référence (simulation)

| Mesure | Valeur |
|---|---|
| 5 Hz commandé -> mesuré (Hz) | 5 |
| 10 Hz commandé -> mesuré (Hz) | 9.999 |
| 20 Hz commandé -> mesuré (Hz) | 20 |
| 40 Hz commandé -> mesuré (Hz) | 40 |
| erreur max (Hz) | 0.001461 |

Verdict : **OK**.

![TP07 en simulation](images/sil.png)

**Lire le graphique.** À gauche : le signal brut (vibration rapide du moteur) et son enveloppe (allumage et extinction). À droite : un pic par fréquence commandée. Les petits pics à 3f et 5f sont les harmoniques normales d'un signal carré.

## 9. Ce qui serait anormal

- Un pic décalé : horloge d'échantillonnage fausse (voir TP10).
- Un pic à une fréquence jamais commandée : repliement de spectre ou résonance mécanique du support.

## 10. Vos résultats sur le vrai capteur

> **À compléter** après la campagne sur le matériel. Ajoutez le graphique, remplissez le tableau et écrivez votre analyse.

**Ce à quoi s'attendre.** Les pics seront plus petits si le moteur est mal fixé ou si le support est souple. Des pics parasites peuvent apparaître (résonance du bras du servo). La fréquence, elle, doit rester juste : elle dépend de l'horloge de l'ESP32, pas de la mécanique.

| Mesure | Simulation | Vrai capteur | Écart / commentaire |
|---|---|---|---|
| 5 Hz commandé -> mesuré (Hz) | 5 | | |
| 10 Hz commandé -> mesuré (Hz) | 9.999 | | |
| 20 Hz commandé -> mesuré (Hz) | 20 | | |
| 40 Hz commandé -> mesuré (Hz) | 40 | | |
| erreur max (Hz) | 0.001461 | | |

<!-- Après la campagne réelle, retirez cette ligne de commentaire et la dernière pour afficher le graphique :
![TP07 sur le vrai capteur](images/hil.png)
-->

**Analyse :** *(Que montrent vos mesures ? Quels écarts avec la simulation, et pourquoi ? Le défaut vient-il du capteur ou du banc ?)*

## 11. Pour aller plus loin

- Ajoutez 120 Hz dans `frequencies_hz` : le test échoue. Expliquez pourquoi avec la fréquence de coupure de l'enveloppe.
- Tracez la FFT du signal brut (sans enveloppe) et retrouvez la porteuse du moteur.

## 12. Questions de révision

**Pourquoi une fenêtre de Hann ?**

<details>
<summary>Réponse</summary>

Pour limiter les fuites spectrales quand la durée d'acquisition n'est pas un multiple exact de la période du signal.

</details>

**Pourquoi faire la FFT de l'enveloppe et pas du signal brut ?**

<details>
<summary>Réponse</summary>

Parce qu'on cherche la fréquence d'allumage du vibreur, pas sa vitesse de rotation. Cette fréquence n'apparaît que dans l'enveloppe.

</details>

## Checklist de fin de TP

- [ ] Test lancé et compris en simulation
- [ ] Test lancé sur le vrai capteur
- [ ] Graphique réel ajouté (`images/hil.png`) et affiché ci-dessus
- [ ] Tableau des résultats réels rempli
- [ ] Analyse rédigée
- [ ] Statut mis à jour ici et dans le [sommaire](../../../README.md#parcours)

---

[← TP06](../TP06-repetabilite/README.md) · [Sommaire du module](../README.md) · [TP08 →](../TP08-temps-de-reponse/README.md)
