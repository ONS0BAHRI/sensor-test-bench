[Formation](../../README.md) › Module 3

# Module 3 · Le simulateur (SIL)

**Statut :** à faire

Le simulateur reproduit le banc complet, avec ses défauts. Il permet de développer et de valider toute la chaîne de test avant d'avoir le matériel, puis de rejouer les tests à volonté dans l'intégration continue.

## 1. L'interface commune

Toutes les procédures de test utilisent les mêmes méthodes, définies dans [`bench/base.py`](../../bench/base.py) :

| Méthode | Rôle |
|---|---|
| `identify()` | Lit le registre WHO_AM_I |
| `set_angle(angle)` | Incline le capteur (servo) |
| `set_vibration(freq)` | Module le vibreur à `freq` Hz (0 = arrêt) |
| `read(n)` | Acquiert n mesures horodatées |
| `step(angle, n)` | Acquiert n mesures en commandant un échelon d'angle pendant l'acquisition |
| `wait(s)` | Attend la stabilisation |

`SimulatedSensor` ([`bench/simulated_sensor.py`](../../bench/simulated_sensor.py)) et `RealSensor` ([`bench/real_sensor.py`](../../bench/real_sensor.py)) implémentent ces méthodes. On choisit l'un ou l'autre avec `open_bench("sil")` ou `open_bench("hil", port)`.

```python
from bench import open_bench

with open_bench("sil") as bench:          # ou open_bench("hil", "COM3")
    bench.set_angle(30)
    bench.wait(0.4)
    m = bench.read(500)
    print(m.ax.mean())                    # ≈ sin(30°) = 0,5 g, plus l'offset et l'erreur de gain
```

## 2. Un simulateur volontairement imparfait

Un simulateur parfait ne servirait à rien : aucun test ne pourrait échouer. Celui-ci reproduit les défauts qu'un banc doit détecter, avec des ordres de grandeur réalistes.

| Imperfection | Paramètre | Valeur par défaut | TP concerné |
|---|---|---|---|
| Offset par axe | `offset_g` | 35, −20, 60 mg | TP02 |
| Erreur de gain par axe | `gain` | 1,020 ; 1,000 ; 0,985 | TP04 |
| Bruit blanc | `noise_std_g` | 4 mg | TP03, TP09 |
| Quantification | fixe | 1/16384 g (16 bits à ±2 g) | TP03 |
| Vitesse du servo | `servo_speed_dps` | 600 °/s (0,1 s pour 60°) | TP08 |
| Jeu mécanique du servo | `backlash_deg` | 0,4° | TP05 |
| Erreur de position du servo | `servo_error_deg` | 0,3° | TP04 |
| Porteuse du vibreur | `vib_carrier_hz` | 170 Hz | TP07 |
| Temps de montée du moteur | `vib_tau_s` | 15 ms | TP07 |
| Gigue d'horodatage | fixe | 15 µs | TP10 |

## 3. Régler le simulateur depuis la ligne de commande

```bash
python run_bench.py --noise 0.012       # bruit de 12 mg
python run_bench.py --offset-x 0.2      # offset de 200 mg sur X
python run_bench.py --backlash 1.0      # jeu de 1° sur le servo
python run_bench.py --seed 7            # autre tirage du bruit
python run_bench.py --defective         # plusieurs défauts à la fois
```

## 4. Exercices

1. **Capteur trop bruité.** Lancez `--noise 0.012`. Quel test passe KO ? Trouvez la valeur exacte de bascule et reliez-la au seuil de `limits.yaml`.
2. **Gros offset.** Lancez `--offset-x 0.2`. TP02 passe KO, mais TP04 reste OK. Expliquez pourquoi.
3. **Servo usé.** Calculez le jeu maximal toléré pour rester sous 20 mg d'hystérésis (à 0°, 1° donne environ 17,5 mg ; l'écart montée / descente vaut deux fois le jeu). Vérifiez avec `--backlash`.
4. **Reproductibilité du simulateur.** Lancez deux fois la même commande, puis avec `--seed 7`. Que change la graine ?

<details>
<summary>Éléments de réponse</summary>

1. TP03 : l'écart-type mesuré suit le paramètre de bruit, la bascule se fait vers 10 mg.
2. Un offset constant décale toute la droite sans la déformer : la linéarité n'est pas affectée.
3. 20 mg ÷ (2 × 17,5 mg/°) ≈ 0,57°. Le simulateur donne OK à 0,55° et KO à 0,6°.
4. Même graine, mêmes résultats : c'est indispensable pour que l'intégration continue soit déterministe.

</details>

## Vos résultats

> **À compléter :** notez pour chaque exercice la commande, le résultat et votre explication en une phrase.

| Exercice | Commande | Résultat | Explication |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |

## Checklist

- [ ] Je sais expliquer le rôle de l'interface commune
- [ ] Les quatre exercices sont faits et notés

---

[← Module 2 · Installation](../02-installation/README.md) · [Sommaire](../../README.md) · [Module 4 · Traitement du signal →](../04-traitement-du-signal/README.md)
