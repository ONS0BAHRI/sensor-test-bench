[Formation](../../../README.md) › [5 · Tests du capteur](../README.md) › TP12

# TP12 · Robustesse aux erreurs

**Statut :** à faire

| | |
|---|---|
| **Objectif** | Vérifier que le banc signale chaque erreur proprement et ne plante jamais. |
| **Procédure** | `t12_robustesse` dans [`bench/procedures.py`](../../../bench/procedures.py) |
| **Modes** | simulation (SIL) et vrai capteur (HIL) |

## 1. Pourquoi ce test

En production, un banc tourne des milliers de fois. Il doit signaler une panne clairement, continuer la séquence et ne jamais bloquer la ligne.

## 2. Notions à connaître

- Gestion des exceptions : chaque erreur prévue a un type précis (`ValueError` pour un mauvais argument, `SensorError` pour un problème matériel).
- Protocole robuste : le firmware répond toujours, soit avec le résultat, soit avec `ERR <message>`.
- Un test qui plante est enregistré comme KO avec son message ; la campagne continue.

## 3. Conditions de mesure

Aucune condition particulière.

## 4. Méthode

1. Demander un angle hors plage (200°) : `ValueError` attendue.
2. Demander une acquisition de 0 point : `ValueError` attendue.
3. Envoyer une commande inconnue : `SensorError` attendue (réponse `ERR` du firmware).
4. En simulation : simuler un capteur débranché, `SensorError` attendue.
5. Vérifier que le banc répond toujours normalement après ces erreurs.

## 5. Le code

La procédure pilote le banc, calcule les indicateurs et compare aux seuils. Elle est identique en simulation et sur le vrai capteur.

<details>
<summary>Voir le code de <code>t12_robustesse</code></summary>

```python
def t12_robustesse(bench: SensorInterface, lim: dict) -> TestResult:
    checks = {}

    def expect(name, exc_type, fn):
        try:
            fn()
            checks[name] = "KO : aucune erreur levée"
        except exc_type as exc:
            checks[name] = f"OK : {type(exc).__name__}"
        except Exception as exc:  # erreur non prévue = plantage mal géré
            checks[name] = f"KO : {type(exc).__name__} inattendue ({exc})"

    expect("angle hors plage (200°)", ValueError, lambda: bench.set_angle(200))
    expect("acquisition de 0 point", ValueError, lambda: bench.read(0))
    expect("commande série inconnue", SensorError, lambda: bench.raw_command("FOO"))
    if bench.mode == "sil":
        expect("capteur débranché", SensorError, lambda: SimulatedSensor(disconnected=True).identify())
    still_ok = bench.identify() == lim["T01_communication"]["who_am_i"]
    checks["banc toujours opérationnel après les erreurs"] = "OK" if still_ok else "KO"
    passed = all(v.startswith("OK") for v in checks.values())
    return TestResult("T12", "Robustesse aux erreurs", passed,
                      "chaque erreur est signalée proprement, sans plantage", checks,
                      notes="En HIL, le débranchement du câble se teste à la main (voir README).")
```

</details>

## 6. Critère d'acceptation

Critère vérifié : **chaque erreur est signalée proprement, sans plantage**.

## 7. Lancer le TP

```bash
pytest tests/test_bench.py -k t12 -s                         # simulation
pytest tests/test_bench.py -k t12 -s --mode hil --port COM3  # vrai capteur (Linux : /dev/ttyUSB0)
python run_bench.py --mode hil --port COM3 --docs              # campagne complète, graphiques rangés dans les TP
```

## 8. Résultat de référence (simulation)

| Mesure | Valeur |
|---|---|
| angle hors plage (200°) | OK : ValueError |
| acquisition de 0 point | OK : ValueError |
| commande série inconnue | OK : SensorError |
| capteur débranché | OK : SensorError |
| banc toujours opérationnel après les erreurs | OK |

Verdict : **OK**.

## 9. Ce qui serait anormal

- Une exception d'un autre type : erreur non prévue, à traiter dans le code.
- Le banc ne répond plus après une erreur : le protocole s'est désynchronisé.

## 10. Vos résultats sur le vrai capteur

> **À compléter** après la campagne sur le matériel. Ajoutez le graphique, remplissez le tableau et écrivez votre analyse.

**Ce à quoi s'attendre.** Testez aussi à la main : débranchez le fil SDA pendant une campagne. Le test en cours doit passer KO avec le message `ERR lecture I2C impossible`, et les suivants doivent continuer.

| Mesure | Simulation | Vrai capteur | Écart / commentaire |
|---|---|---|---|
| angle hors plage (200°) | OK : ValueError | | |
| acquisition de 0 point | OK : ValueError | | |
| commande série inconnue | OK : SensorError | | |
| capteur débranché | OK : SensorError | | |
| banc toujours opérationnel après les erreurs | OK | | |

**Analyse :** *(Que montrent vos mesures ? Quels écarts avec la simulation, et pourquoi ? Le défaut vient-il du capteur ou du banc ?)*

## 11. Pour aller plus loin

- Coupez le câble USB pendant une acquisition et vérifiez le message d'erreur côté PC.
- Ajoutez un test pour une réponse tronquée du firmware (bloc de données incomplet).

## 12. Questions de révision

**Que se passe-t-il si un test plante pendant la campagne ?**

<details>
<summary>Réponse</summary>

Il est noté KO avec son message d'erreur et la campagne continue : on veut le diagnostic complet du capteur, pas un arrêt au premier problème.

</details>

**Pourquoi deux types d'erreur différents ?**

<details>
<summary>Réponse</summary>

Pour distinguer une erreur d'utilisation (mauvais paramètre, à corriger dans le code) d'une panne matérielle (capteur, câble, à réparer sur le banc).

</details>

## Checklist de fin de TP

- [ ] Test lancé et compris en simulation
- [ ] Test lancé sur le vrai capteur
- [ ] Tableau des résultats réels rempli
- [ ] Analyse rédigée
- [ ] Statut mis à jour ici et dans le [sommaire](../../../README.md#parcours)

---

[← TP11](../TP11-derive-thermique/README.md) · [Sommaire du module](../README.md) · [TP13 →](../TP13-detection-de-defauts/README.md)
