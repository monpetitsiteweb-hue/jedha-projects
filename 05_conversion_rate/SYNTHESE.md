# Conversion : synthèse du projet

**Bloc 3, projet déposé sans présentation.** Challenge de prédiction : dire si un visiteur du site va s'abonner, avec le f1-score comme métrique, puis en tirer des recommandations pour améliorer la conversion.

## Données

- **Volume :** 284 580 lignes étiquetées et 31 620 lignes à prédire (c9).
- **Cible :** 3,23 % de conversions (c10). Une telle cible rend l'accuracy inutile, d'où le f1-score (c11).
- **Qualité :** aucune valeur manquante. Les 268 769 doublons sont gardés, car des visiteurs différents peuvent avoir le même profil (c10).
- **Échantillon :** les taux par groupe sont calculés sur toutes les lignes (c13, c14) : un taux agrégé ne trace qu'un point par groupe, donc échantillonner n'allégerait pas le graphique et rendrait le taux moins précis.
- **Nettoyage :** 2 lignes retirées, avec des âges impossibles de 111 et 123 ans (c12, c17).
- **Découpage :** 256 120 lignes d'entraînement et 28 458 de test, stratifiées (c19).

## Résultats des modèles

| Modèle | Seuil | f1 en validation croisée (c32) | f1 sur le test (c32) |
|---|---:|---:|---:|
| Baseline : régression logistique, pages seules | 0,50 | non calculé | 0,6961 |
| Régression logistique, toutes variables | 0,50 | non calculé | 0,7712 |
| **Régression logistique, toutes variables (retenue)** | **0,40** | **0,7708** | **0,7668** |
| Régression logistique avec termes de degré 2 | 0,41 | 0,7698 | 0,7627 |
| Gradient boosting | 0,43 | 0,7684 | 0,7707 |

- **Choix :** le modèle est retenu sur la validation croisée, et non sur le jeu de test (c33). Sur le test, il a une précision de 0,8024 et un rappel de 0,7342 (c33).
- **Matrice de confusion sur le test :** 674 conversions trouvées, 244 manquées, 166 fausses alertes (c33).

## Fichiers de soumission

Les deux fichiers sont **prêts et conformes**. Cette synthèse n'affirme pas qu'ils ont été envoyés au classement, et aucun score de classement n'est connu.

| Fichier, dans `05_conversion_rate\submissions\` | Lignes | Taux prédit (c35) |
|---|---:|---:|
| `conversion_data_test_predictions_CARLOS-logreg.csv` | 31 620 | 2,91 % |
| `conversion_data_test_predictions_CARLOS-gradient-boosting.csv` | 31 620 | 2,79 % |

Chaque fichier a une seule colonne `converted`, sans index, et autant de lignes que le jeu à prédire (c35 ne relit que le dernier fichier écrit, le contrôle des 2 CSV donne le même résultat). Les deux modèles sont réentraînés sur les données étiquetées conservées, soit 284 578 lignes sur 284 580, avant la prédiction (c17, c35).

## Facteurs liés à la conversion

| Facteur | Taux de conversion (c13, c14) | Effet sur les chances, à profil comparable (c38) |
|---|---|---|
| Pages visitées | 6,0 % à 10 pages, 99,7 % à 20 pages | ×2,13 par page en plus |
| Visiteur nouveau ou non | 1,41 % contre 7,19 % | ×0,18 pour un nouveau visiteur |
| Pays | Chine 0,13 %, États-Unis 3,79 %, Royaume-Uni 5,25 %, Allemagne 6,24 % | Par rapport à la Chine : ×19,9, ×27,9, ×34,9 |
| Âge | Baisse avec l'âge | ×0,48 pour 10 ans de plus |
| Source | Ads 3,48 %, Seo 3,29 %, Direct 2,78 % | Par rapport à Ads : Seo ×0,98, Direct ×0,81 |

**Principal constat :** le nombre de pages visitées est le signal le plus fort, et la conversion bascule entre 10 et 20 pages (c14, c16).

## Recommandations (c39)

- Encourager la navigation et placer l'appel à l'abonnement là où se trouvent les lecteurs engagés.
- Faire revenir les visiteurs.
- Vérifier l'accès au site et au formulaire depuis la Chine, ainsi que la langue des contenus.
- Arbitrer entre Ads et Seo sur le coût par visiteur, car la source change peu la conversion.

## Limites

- **Causalité :** ce sont des associations apprises par le modèle, à confirmer par des tests A/B (c39).
- **Modèles proches :** sur le test, les écarts entre les quatre modèles améliorés sont faibles, de 0,7627 à 0,7712 (c32).
