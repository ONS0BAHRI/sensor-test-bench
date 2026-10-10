[Formation](../../../README.md) › [5 · Tests du capteur](../README.md) › TP10

# TP10 · Fréquence d'échantillonnage réelle

**Statut :** à faire

| | |
|---|---|
| **Objectif** | Vérifier que la cadence d'acquisition réelle est bien celle annoncée. |
| **Procédure** | `t10_echantillonnage` dans [`bench/procedures.py`](../../../bench/procedures.py) |
| **Seuils** | section `T10_echantillonnage` de [`config/limits.yaml`](../../../config/limits.yaml) |
| **Modes** | simulation (SIL) et vrai capteur (HIL) |

## 1. Pourquoi ce test

Toutes les analyses en temps et en fréquence supposent une cadence exacte. Un microcontrôleur surchargé peut échantillonner moins vite qu'annoncé, sans aucun message d'erreur.

## 2. Notions à connaître

- Période d'échantillonnage : 1 / fe = 2 000 µs à 500 Hz.
- Gigue (jitter) : variation de la période d'un échantillon à l'autre.
- Horodatage côté microcontrôleur : chaque mesure est datée au moment où elle est prise.

## 3. Conditions de mesure

Acquisition de 2 000 mesures horodatées en microsecondes par l'ESP32.

## 4. Méthode

1. Calculer les écarts entre horodatages successifs.
2. Fréquence réelle = 1 / moyenne des écarts ; gigue = écart-type / moyenne.
3. Comparer à la fréquence nominale.

## 5. Le code

La procédure pilote le banc, calcule les indicateurs et compare aux seuils. Elle est identique en simulation et sur le vrai capteur.

<details>
<summary>Voir le code de <code>t10_echantillonnage</code></summary>

```python
def t10_echantillonnage(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T10_echantillonnage"]
    m = bench.read(c["n"])
    rate, jitter = sp.effective_sample_rate(m.t_us)
    err = abs(rate - bench.sample_rate) / bench.sample_rate * 100
    passed = err <= c["max_rate_error_pct"] and jitter <= c["max_jitter_pct"]
    return TestResult("T10", "Fréquence d'échantillonnage réelle", passed,
                      f"écart ≤ {c['max_rate_error_pct']} % et gigue ≤ {c['max_jitter_pct']} %",
                      {"fréquence nominale (Hz)": bench.sample_rate, "fréquence mesurée (Hz)": rate,
                       "écart (%)": err, "gigue (%)": jitter},
                      {"dt_us": np.diff(m.t_us)})
```

</details>

## 6. Critère d'acceptation

Extrait de `config/limits.yaml` :

```yaml
T10_echantillonnage:
  n: 2000
  max_rate_error_pct: 5.0
  max_jitter_pct: 5.0
```

Critère vérifié : **écart ≤ 5.0 % et gigue ≤ 5.0 %**.

## 7. Lancer le TP

```bash
pytest tests/test_bench.py -k t10 -s                         # simulation
pytest tests/test_bench.py -k t10 -s --mode hil --port COM3  # vrai capteur (Linux : /dev/ttyUSB0)
python run_bench.py --mode hil --port COM3 --docs              # campagne complète, graphiques rangés dans les TP
```

## 8. Résultat de référence (simulation)

| Mesure | Valeur |
|---|---|
| fréquence nominale (Hz) | 500 |
| fréquence mesurée (Hz) | 500 |
| écart (%) | 0.0006253 |
| gigue (%) | 1.007 |

Verdict : **OK**.

![TP10 en simulation](images/sil.png)

**Lire le graphique.** L'histogramme des périodes doit être étroit et centré sur 2 000 µs.

## 9. Ce qui serait anormal

- Une deuxième bosse vers 4 000 µs : des échantillons ont été perdus.
- Une distribution large : gigue importante, la boucle d'acquisition est perturbée.

## 10. Vos résultats sur le vrai capteur

> **À compléter** après la campagne sur le matériel. Ajoutez le graphique, remplissez le tableau et écrivez votre analyse.

**Ce à quoi s'attendre.** Avec le firmware qui stocke d'abord les mesures puis les envoie, la cadence réelle doit être très stable. Si vous modifiez le firmware pour envoyer pendant l'acquisition, refaites ce TP : c'est exactement ce genre de régression qu'il détecte.

| Mesure | Simulation | Vrai capteur | Écart / commentaire |
|---|---|---|---|
| fréquence nominale (Hz) | 500 | | |
| fréquence mesurée (Hz) | 500 | | |
| écart (%) | 0.0006253 | | |
| gigue (%) | 1.007 | | |

<!-- Après la campagne réelle, retirez cette ligne de commentaire et la dernière pour afficher le graphique :
![TP10 sur le vrai capteur](images/hil.png)
-->

**Analyse :** *(Que montrent vos mesures ? Quels écarts avec la simulation, et pourquoi ? Le défaut vient-il du capteur ou du banc ?)*

## 11. Pour aller plus loin

- Ajoutez un `delay(1)` dans la boucle d'acquisition du firmware et observez le résultat.
- Calculez le nombre de mesures perdues à partir des horodatages.

## 12. Questions de révision

**Pourquoi horodater dans l'ESP32 et pas sur le PC ?**

<details>
<summary>Réponse</summary>

Parce que l'USB transmet les données par paquets : l'heure d'arrivée sur le PC ne reflète pas l'instant de la mesure.

</details>

**Que devient une FFT si la fréquence réelle est fausse ?**

<details>
<summary>Réponse</summary>

Toutes les fréquences trouvées sont fausses du même facteur : un pic à 10 Hz pourrait apparaître à 9,5 Hz.

</details>

## Checklist de fin de TP

- [ ] Test lancé et compris en simulation
- [ ] Test lancé sur le vrai capteur
- [ ] Graphique réel ajouté (`images/hil.png`) et affiché ci-dessus
- [ ] Tableau des résultats réels rempli
- [ ] Analyse rédigée
- [ ] Statut mis à jour ici et dans le [sommaire](../../../README.md#parcours)

---

[← TP09](../TP09-filtre-numerique/README.md) · [Sommaire du module](../README.md) · [TP11 →](../TP11-derive-thermique/README.md)
