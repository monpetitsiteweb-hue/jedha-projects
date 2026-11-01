# Uber : synthèse du projet

**Bloc 3, projet déposé sans présentation.** Recommander aux chauffeurs de New York les zones où la demande est la plus forte, pour chaque jour de la semaine et chaque heure, en comparant au moins deux algorithmes non supervisés.

## Données

- **Source :** zip fourni par Jedha, six fichiers d'avril à septembre 2014, soit 4 534 327 courses (c6).
- **Nettoyage :** aucune valeur manquante (c7), 17 771 courses retirées hors de la zone de New York, soit 0,39 % (c9). La zone garde la métropole et ses trois aéroports, dont Newark, hors de la ville de New York (c8) : ces aéroports sont des lieux de prise en charge liés aux trajets vers la ville.

## Quand se situe la demande

- **Par mois :** de 563 127 courses en avril à 1 023 898 en septembre (c11).
- **Par jour :** jeudi 28 946 courses par jour en moyenne, vendredi 28 388, dimanche 18 766 (c12).
- **Par heure :** maximum le jeudi à 17h avec 2 174 courses par heure en moyenne, minimum le mardi à 2h avec 95 (c13).

## Comparaison sur un créneau de référence

Lundi de 17h à 18h : 41 905 courses, dont un échantillon de 10 000 points (c20). La couverture est la part des courses à moins de 1 km du centre d'une zone (c31).

| Algorithme (c32) | Zones | Bruit | Silhouette, hors bruit | Couverture à 1 km |
|---|---:|---:|---:|---:|
| KMeans, k = 10 | 10 | 0,0 % | 0,434 | 52,2 % |
| DBSCAN, eps = 200 m, min_samples = 0,5 % | 13 | 36,5 % | 0,165 | 55,8 % |
| HDBSCAN, en bonus | 17 | 61,6 % | 0,595 | 76,4 % |

**Choix de k :** la silhouette est la plus haute à k = 5 (0,506), mais si peu de zones ne servent à rien pour un chauffeur. k = 10 donne des zones de la taille d'un quartier (c22, c23).

## Résultats sur les 168 créneaux

KMeans et DBSCAN tournent sur 7 jours × 24 heures, soit 336 regroupements et 4 324 zones (c34).

| Méthode (c35, c37) | Zones en moyenne | Couverture moyenne à 1 km | Couverture minimale |
|---|---:|---:|---:|
| KMeans, k = 10 | 10,0 | 38,9 % | 19,1 % |
| KMeans, autant de zones que DBSCAN | 15,7 | 51,9 % | non calculé |
| DBSCAN | 15,7, de 6 à 36 | 56,1 % | 24,7 % |

**Principal constat :** à nombre de zones égal, DBSCAN couvre un peu plus de courses (56,1 % contre 51,9 %), mais il laisse en moyenne 50,3 % des points en bruit (c35, c37).

## Zones chaudes, avec KMeans

| Période (c47) | Quatre premières zones nommées |
|---|---|
| Lundi à jeudi, heures 7, 8, 17 et 18 | SoHo, Grand Central / Midtown East, Upper East Side, Union Square |
| Vendredi et samedi, heures 22, 23, 0, 1 et 2 de ces deux jours | SoHo, Times Square / Midtown West, Williamsburg, Chelsea / Meatpacking |

Le filtre de nuit prend ces heures dans les mêmes jours du calendrier : il inclut la fin de la nuit de jeudi et laisse la fin de celle de samedi.

Pic par couple zone-heure (c41) : SoHo le vendredi à 22h, environ 833 courses par heure, et Times Square / Midtown West le mercredi à 17h, environ 711. Les zones doivent donc être calculées par jour **et** par heure (c14).

## Choix techniques

- **Ordre de lecture :** les fichiers mensuels sont lus dans l'ordre alphabétique, car l'échantillon tiré dépend de l'ordre des lignes.
- **numexpr :** il est désactivé, car il renvoyait par moments des sélections vides dans Anaconda base, ce qui faisait échouer KMeans.

## Limites

- **Données :** 6 mois de 2014, seulement des courses, sans l'offre de chauffeurs ni les temps d'attente. Les zones montrent la demande, pas l'écart entre la demande et l'offre (c53).
- **DBSCAN :** un seul `eps` pour toute la ville et une très grande zone fusionnée dans Manhattan aux heures chargées, 40,7 % des points le lundi à 17h (c28, c53).
- **Couverture :** l'équivalence entre 1 km et 4 à 6 minutes de trajet est une hypothèse du notebook, pas une mesure (c31).

## Où trouver quoi

- **Notebook et export HTML :** `06_uber\notebooks\`
- **Cartes :** `06_uber\maps\`
- **Tableau de bord et ses données :** `06_uber\dashboard\`
