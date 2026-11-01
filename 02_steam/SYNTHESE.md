# Steam : synthèse du projet

**Bloc 2, projet déposé sans présentation.** Pour Ubisoft, analyse du catalogue Steam avec PySpark et les visualisations de Databricks. Comme la publication n'existe plus sur Databricks, les sorties sont livrées en exports et en captures d'écran.

## Données

- **Source :** `s3://full-stack-bigdata-datasets/Big_Data/Project_Steam/steam_game_output.json`, lu dans `setup_data` c2.
- **Volume :** 55 691 enregistrements, 55 690 jeux après nettoyage (`00` c4 et c11).
- **Champs vides :** 134 éditeurs, 127 développeurs, 161 genres et 11 langues (`00` c8).

## Résultats

| Thème | Résultat | Cellule |
|---|---|---|
| Éditeurs | 29 833 valeurs d'éditeur, listes d'éditeurs non séparées, dont 77 % avec un seul jeu ; les 20 premiers font 4,9 % des jeux | `01` c5 |
| Premier éditeur | Big Fish Games, 423 jeux | `01` c28 |
| Ubisoft | 127 jeux, dont 55,1 % en Action et 35,4 % en Adventure | `02` c11 |
| Sorties | Pic en 2021 parmi les années complètes, avec 8 823 jeux | `01` c28 |
| Covid | Croissance de -9,2 % en 2019, 19,2 % en 2020, 6,2 % en 2021 | `01` c16 |
| Prix | 14,0 % de jeux gratuits ; jeux payants à 5,99 $ en médiane et 8,99 $ en moyenne | `01` c18, c28 |
| Remises | 5,3 % des jeux payants remisés au moment de l'extraction | `01` c20 |
| Langues | Anglais 99,0 %, allemand 25,2 %, français 24,1 % | `01` c28 |
| Âge | 0,5 % des jeux réservés aux 16 ans et plus | `01` c28 |
| Genres | Indie 71,3 %, Action 42,7 %, Casual 39,7 % | `02` c18 |
| Avis | Animation & Modeling 96,3 % de positifs ; Massively Multiplayer 73,1 % | `02` c18 |
| Revenu estimé | Action en tête du total, avec 58 756,5 M$ | `02` c18 |
| Plateformes | Windows 100,0 %, Mac 22,9 %, Linux 15,2 % | `03` c26 |

## Facteurs liés à la popularité

Part des jeux à 100 000 propriétaires ou plus :

| Facteur | Un groupe bas | Un groupe haut | Cellule |
|---|---|---|---|
| Prix | 5,89 % sous 5 $, hors gratuits (20,0 %) | 31,91 % de 20 à 40 $ (maximum : 32,45 % à 40 $ ou plus) | `03` c12 |
| Langues | 7,01 % avec 0 ou 1 langue (minimum : 6,88 % avec 2 ou 3) | 30,29 % avec 11 langues ou plus | `03` c14 |
| Plateformes | 10,0 % avec 1 plateforme | 21,25 % avec 3 plateformes | `03` c16 |

Corrélations avec le logarithme des propriétaires (`03` c24) : logarithme du nombre d'avis 0,779, âge du jeu 0,376, langues 0,215, prix 0,139, plateformes 0,138, part d'avis positifs 0,085.

**Principal constat :** le nombre de propriétaires est très lié au logarithme du nombre d'avis (0,779), mais presque pas à la part d'avis positifs (0,085).

## Limites

- **Revenus :** c'est une estimation, propriétaires multipliés par prix actuel, et non des ventes. Le revenu moyen de Massively Multiplayer (4 061,8 k$ par jeu) cache une médiane de 0,0 (`02` c13).
- **Propriétaires :** le fichier donne des fourchettes, pas des chiffres exacts.
- **Corrélations :** elles ne prouvent aucune cause. Le nombre d'avis suit logiquement le nombre de propriétaires, et les jeux anciens ont eu plus de temps pour en gagner.
- **2022 :** l'année est incomplète, la dernière sortie date du 2022-11-11 (`01` c13).

## Où trouver quoi

- **Notebooks avec sorties :** `02_steam\notebooks\`
- **Exports HTML et `.ipynb` :** `02_steam\captures\`
- **22 captures :** `02_steam\captures\LISTE-CAPTURES.md`
