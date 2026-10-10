[Formation](../../../README.md) › [5 · Tests du capteur](../README.md) › TP01

# TP01 · Communication I2C

**Statut :** à faire

| | |
|---|---|
| **Objectif** | Vérifier que le capteur répond sur le bus I2C avant de lancer la moindre mesure. |
| **Procédure** | `t01_communication` dans [`bench/procedures.py`](../../../bench/procedures.py) |
| **Seuils** | section `T01_communication` de [`config/limits.yaml`](../../../config/limits.yaml) |
| **Modes** | simulation (SIL) et vrai capteur (HIL) |

## 1. Pourquoi ce test

C'est toujours la première étape d'une séquence de test. Si le capteur ne répond pas, tous les résultats suivants sont faux : on évite ainsi de chercher un défaut de mesure alors que le problème est un câble, une adresse ou une alimentation.

## 2. Notions à connaître

- Bus I2C : deux fils (SDA pour les données, SCL pour l'horloge), un maître (l'ESP32) et des esclaves identifiés par une adresse sur 7 bits.
- Adresse du MPU6050 : 0x68 quand la broche AD0 est à la masse, 0x69 quand elle est à 3,3 V.
- Registre `WHO_AM_I` (0x75) : registre en lecture seule qui contient l'identifiant du composant, 0x68 pour un MPU6050.

## 3. Conditions de mesure

Aucune condition particulière : capteur alimenté et branché.

## 4. Méthode

1. Envoyer la commande `ID?` au firmware.
2. Le firmware lit le registre 0x75 du capteur et renvoie `ID 0x68`, ou `ERR` si le bus ne répond pas.
3. Comparer la valeur reçue à la valeur attendue de `limits.yaml`.

## 5. Le code

La procédure pilote le banc, calcule les indicateurs et compare aux seuils. Elle est identique en simulation et sur le vrai capteur.

<details>
<summary>Voir le code de <code>t01_communication</code></summary>

```python
def t01_communication(bench: SensorInterface, lim: dict) -> TestResult:
    expected = lim["T01_communication"]["who_am_i"]
    value = bench.identify()
    return TestResult("T01", "Communication I2C", value == expected,
                      f"WHO_AM_I = 0x{expected:02X}", {"WHO_AM_I": f"0x{value:02X}"})
```

</details>

## 6. Critère d'acceptation

Extrait de `config/limits.yaml` :

```yaml
T01_communication:
  who_am_i: 0x68
```

Critère vérifié : **WHO_AM_I = 0x68**.

## 7. Lancer le TP

```bash
pytest tests/test_bench.py -k t01 -s                         # simulation
pytest tests/test_bench.py -k t01 -s --mode hil --port COM3  # vrai capteur (Linux : /dev/ttyUSB0)
python run_bench.py --mode hil --port COM3 --docs              # campagne complète, graphiques rangés dans les TP
```

## 8. Résultat de référence (simulation)

| Mesure | Valeur |
|---|---|
| WHO_AM_I | 0x68 |

Verdict : **OK**.

## 9. Ce qui serait anormal

- `0x00` ou `0xFF`, ou une erreur : bus muet (câble SDA/SCL inversé ou débranché, alimentation absente, mauvaise adresse).
- Une autre valeur, par exemple `0x70` : le module porte un autre composant (un MPU6500 est parfois vendu sous l'étiquette GY-521).

## 10. Vos résultats sur le vrai capteur

> **À compléter** après la campagne sur le matériel. Ajoutez le graphique, remplissez le tableau et écrivez votre analyse.

**Ce à quoi s'attendre.** Même résultat attendu. Si vous obtenez une erreur, vérifiez dans l'ordre : alimentation 3,3 V du module, câbles SDA (GPIO21) et SCL (GPIO22), masse commune.

| Mesure | Simulation | Vrai capteur | Écart / commentaire |
|---|---|---|---|
| WHO_AM_I | 0x68 | | |

**Analyse :** *(Que montrent vos mesures ? Quels écarts avec la simulation, et pourquoi ? Le défaut vient-il du capteur ou du banc ?)*

## 11. Pour aller plus loin

- Avec un analyseur logique (quelques euros), capturez la trame I2C de la lecture de `WHO_AM_I` et identifiez l'adresse, le bit de lecture et l'acquittement.
- Reliez AD0 à 3,3 V et observez que le capteur ne répond plus à l'adresse 0x68.

## 12. Questions de révision

**Pourquoi lire `WHO_AM_I` plutôt qu'une mesure ?**

<details>
<summary>Réponse</summary>

Parce que c'est une valeur fixe et connue : si elle est correcte, le bus, l'adresse et l'alimentation sont validés d'un coup. Une mesure, elle, peut varier.

</details>

**Que se passe-t-il si deux capteurs ont la même adresse sur le bus ?**

<details>
<summary>Réponse</summary>

Ils répondent en même temps et les données se mélangent. C'est pour cela que la broche AD0 permet de choisir entre 0x68 et 0x69.

</details>

## Checklist de fin de TP

- [ ] Test lancé et compris en simulation
- [ ] Test lancé sur le vrai capteur
- [ ] Tableau des résultats réels rempli
- [ ] Analyse rédigée
- [ ] Statut mis à jour ici et dans le [sommaire](../../../README.md#parcours)

---

[Sommaire du module](../README.md) · [TP02 →](../TP02-offset-et-calibration/README.md)
