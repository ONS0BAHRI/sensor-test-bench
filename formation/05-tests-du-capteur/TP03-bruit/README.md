[Formation](../../../README.md) › [5 · Tests du capteur](../README.md) › TP03

# TP03 · Bruit au repos

**Statut :** à faire

| | |
|---|---|
| **Objectif** | Quantifier le bruit du capteur, qui fixe la plus petite variation mesurable. |
| **Procédure** | `t03_bruit` dans [`bench/procedures.py`](../../../bench/procedures.py) |
| **Seuils** | section `T03_bruit` de [`config/limits.yaml`](../../../config/limits.yaml) |
| **Modes** | simulation (SIL) et vrai capteur (HIL) |

## 1. Pourquoi ce test

Le bruit limite la résolution utile. Un capteur avec 4 mg de bruit ne peut pas mesurer de façon fiable une inclinaison de 0,05°. C'est un critère de base de toute fiche technique.

## 2. Notions à connaître

- Bruit : variation aléatoire autour de la valeur moyenne, mesurée par l'écart-type.
- SNR (rapport signal sur bruit) en dB : 20·log10(signal / bruit). Ici le signal de référence est 1 g.
- Densité spectrale de bruit : bruit par racine de hertz (la datasheet MPU6050 indique environ 400 µg/√Hz). Plus la bande passante est large, plus le bruit total est grand.
- Bruit blanc : bruit réparti également sur toutes les fréquences ; son spectre est plat.

## 3. Conditions de mesure

Capteur à plat, immobile, vibreur arrêté. 2 000 mesures (4 s à 500 Hz).

## 4. Méthode

1. Acquérir 2 000 mesures au repos.
2. Calculer l'écart-type de chaque axe.
3. Calculer le SNR à partir du pire axe.
4. Calculer le spectre d'amplitude (FFT avec fenêtre de Hann) pour voir si le bruit contient des fréquences particulières.

## 5. Le code

La procédure pilote le banc, calcule les indicateurs et compare aux seuils. Elle est identique en simulation et sur le vrai capteur.

<details>
<summary>Voir le code de <code>t03_bruit</code></summary>

```python
def t03_bruit(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T03_bruit"]
    bench.set_angle(0)
    bench.wait(lim["acquisition"]["settle_s"])
    m = bench.read(c["n"])
    stds = {a: float(np.std(getattr(m, a))) for a in ("ax", "ay", "az")}
    worst = max(stds.values())
    snr = sp.snr_db(1.0, worst)                                  # signal de référence : 1 g
    freqs, amp = sp.spectrum(m.az, bench.sample_rate)
    passed = worst <= c["max_std_g"] and snr >= c["min_snr_db"]
    measures = {f"écart-type {a} (mg)": v * 1000 for a, v in stds.items()}
    measures["SNR pour 1 g (dB)"] = snr
    return TestResult("T03", "Bruit au repos", passed,
                      f"écart-type ≤ {c['max_std_g'] * 1000:.0f} mg et SNR ≥ {c['min_snr_db']} dB",
                      measures, {"az": m.az, "ax": m.ax, "freqs": freqs, "amp": amp}, {"repos": m})
```

</details>

## 6. Critère d'acceptation

Extrait de `config/limits.yaml` :

```yaml
T03_bruit:
  n: 2000
  max_std_g: 0.01
  min_snr_db: 40
```

Critère vérifié : **écart-type ≤ 10 mg et SNR ≥ 40 dB**.

## 7. Lancer le TP

```bash
pytest tests/test_bench.py -k t03 -s                         # simulation
pytest tests/test_bench.py -k t03 -s --mode hil --port COM3  # vrai capteur (Linux : /dev/ttyUSB0)
python run_bench.py --mode hil --port COM3 --docs              # campagne complète, graphiques rangés dans les TP
```

## 8. Résultat de référence (simulation)

| Mesure | Valeur |
|---|---|
| écart-type ax (mg) | 4.011 |
| écart-type ay (mg) | 4.056 |
| écart-type az (mg) | 4.005 |
| SNR pour 1 g (dB) | 47.84 |

Verdict : **OK**.

![TP03 en simulation](images/sil.png)

**Lire le graphique.** À gauche, l'histogramme doit avoir une forme de cloche centrée sur 0 (bruit gaussien). À droite, le spectre doit être globalement plat (bruit blanc).

Le même test sur le capteur simulé défectueux (`python run_bench.py --defective`) passe KO :

![TP03 capteur défectueux](images/defectueux.png)

## 9. Ce qui serait anormal

- Un pic dans le spectre : vibration parasite (ventilateur, servo qui frémit), ou 50 Hz du secteur.
- Un histogramme à deux bosses : le signal saute entre deux états (contact intermittent, choc).

## 10. Vos résultats sur le vrai capteur

> **À compléter** après la campagne sur le matériel. Ajoutez le graphique, remplissez le tableau et écrivez votre analyse.

**Ce à quoi s'attendre.** Attendez-vous à un bruit réel de quelques mg : avec le filtre interne réglé à 184 Hz, 400 µg/√Hz donne plusieurs mg. Un servo SG90 qui tient sa position vibre souvent légèrement : cherchez un pic vers 50 Hz (sa commande se répète toutes les 20 ms).

| Mesure | Simulation | Vrai capteur | Écart / commentaire |
|---|---|---|---|
| écart-type ax (mg) | 4.011 | | |
| écart-type ay (mg) | 4.056 | | |
| écart-type az (mg) | 4.005 | | |
| SNR pour 1 g (dB) | 47.84 | | |

<!-- Après la campagne réelle, retirez cette ligne de commentaire et la dernière pour afficher le graphique :
![TP03 sur le vrai capteur](images/hil.png)
-->

**Analyse :** *(Que montrent vos mesures ? Quels écarts avec la simulation, et pourquoi ? Le défaut vient-il du capteur ou du banc ?)*

## 11. Pour aller plus loin

- Refaites la mesure servo débranché, capteur posé sur la table : la différence montre la part de bruit due au banc.
- Modifiez le filtre interne du MPU6050 dans le firmware (registre CONFIG, 0x1A) et observez l'effet sur le bruit.

## 12. Questions de révision

**Comment réduire le bruit ?**

<details>
<summary>Réponse</summary>

En moyennant plusieurs mesures ou en filtrant. On gagne en bruit, mais on perd en temps de réponse : c'est un compromis.

</details>

**Pourquoi utiliser une fenêtre de Hann avant la FFT ?**

<details>
<summary>Réponse</summary>

Pour limiter les fuites spectrales : sans fenêtre, l'énergie d'une fréquence s'étale sur les fréquences voisines.

</details>

## Checklist de fin de TP

- [ ] Test lancé et compris en simulation
- [ ] Test lancé sur le vrai capteur
- [ ] Graphique réel ajouté (`images/hil.png`) et affiché ci-dessus
- [ ] Tableau des résultats réels rempli
- [ ] Analyse rédigée
- [ ] Statut mis à jour ici et dans le [sommaire](../../../README.md#parcours)

---

[← TP02](../TP02-offset-et-calibration/README.md) · [Sommaire du module](../README.md) · [TP04 →](../TP04-linearite/README.md)
