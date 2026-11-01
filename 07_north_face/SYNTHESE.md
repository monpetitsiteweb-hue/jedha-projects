# North Face : synthèse du projet

**Bloc 3, projet déposé sans présentation.** À partir des descriptions de produits, créer des groupes de produits similaires, un système de recommandation et une extraction de thèmes, pour le site et l'équipe marketing.

## Données

- **Volume :** 500 produits, deux colonnes (`id`, `description`), aucune valeur manquante (c4).
- **Longueur :** 137 mots par description en médiane, de 47 à 472, en découpant sur les espaces, balises HTML comprises (c5).
- **Point d'attention :** le fichier local est identique au fichier Kaggle désigné par l'énoncé, mais il décrit des produits Patagonia : des descriptions citent Patagonia, aucune The North Face. Ce n'est pas une erreur de collecte, c'est le contenu du jeu de données officiel.

## Méthode

1. **Nettoyage :** retrait des balises HTML, lettres seules, minuscules, lemmatisation avec spaCy, retrait des mots vides (c7, c9).
2. **TF-IDF :** matrice de 500 produits sur 2 051 mots (c11).
3. **Regroupement :** DBSCAN avec la distance cosinus, sur une grille de 21 combinaisons de paramètres (c13).
4. **Recommandation :** `find_similar_items(item_id)` renvoie jusqu'à 5 identifiants du même groupe (c23, c24).
5. **Thèmes :** LSA avec TruncatedSVD, résultat dans `topic_encoded_df` (c31).

## Résultats du regroupement

**Choix :** `eps` = 0,65 et `min_samples` = 4 donnent **18 groupes et 71 produits isolés, soit 14 %** (c16).

| `eps`, avec `min_samples` = 4 (c13) | Groupes | Produits isolés | Plus grand groupe |
|---:|---:|---:|---:|
| 0,60 | 29 | 137 | 92 |
| **0,65** | **18** | **71** | **158** |
| 0,70 | 13 | 17 | 363 |

Au-delà, un groupe géant absorbe presque tout le catalogue : 478 produits à `eps` = 0,75 (c13).

**Exemples de groupes, d'après leurs mots les plus marquants (c20) :**
- **Groupe 1, le plus grand, 158 produits :** pocket, inseam, dwr, water.
- **Groupe 6, 59 produits :** shirt, ringspun, print.
- **Groupe 10, 4 produits :** web, buckle, belt.

## Recommandation

- **Règle :** jusqu'à 5 produits du même groupe, classés par similarité cosinus. Pour les 18 produits des groupes de moins de 6 produits (groupes 10, 11, 12 et 15), la fonction renvoie tous les autres produits du groupe, soit 3 ou 4 identifiants, car l'énoncé demande des identifiants du même groupe. Un produit isolé reçoit ses 5 plus proches voisins dans tout le catalogue (c23, c24).
- **Exemple :** le produit 1, Active classic boxers, renvoie 19, 494, 365, 2 et 495, avec une similarité de 0,48 à 0,30 (c24, c25).
- **Démonstration :** le notebook affiche les 5 produits similaires du produit 5, avec un identifiant fixe, pour que la sortie reste enregistrée (c26, c27). La saisie par l'utilisateur demandée par l'énoncé reste dans `recommender.py`, car `input()` ne laisse aucune sortie dans un notebook exécuté sans clavier.

## Thèmes

**15 thèmes** sont retenus, dans la plage de 10 à 20 demandée. La variance expliquée grimpe lentement, donc le choix se fait sur la lisibilité (c30). Le thème 0 est le thème principal de 224 produits : c'est le vocabulaire générique du catalogue (c32, c35).

Les autres thèmes font ressortir des types de produits et des matières. Leurs comptes incluent des produits dont le poids sur le thème est négatif (c32, c35) :
- **Thème 1, 62 produits :** shirt, ringspun, print.
- **Thème 2, 39 produits :** merino, odor, wool.
- **Thème 7, 31 produits :** strap, mesh, compartment.

**Principal constat :** les groupes rapprochent des familles de produits, avec des mélanges : le groupe 0 réunit sous-vêtements et t-shirts (c20, c25). Les thèmes font aussi ressortir des types de produits, des matières et des usages, ces deux derniers étant utilisables comme filtres de navigation (c41).

## Limites

- **Corpus :** seulement 500 produits, et une représentation sans ordre des mots ni synonymes (c41).
- **Sensibilité :** DBSCAN dépend fortement de `eps` (c13, c41).
- **Produits presque identiques :** les produits 5 et 308 portent le même nom, avec une similarité arrondie à 1,00 ; leurs textes diffèrent (c27).
- **LSA :** les poids peuvent être négatifs, ce qui rend les thèmes moins faciles à lire (c32, c41).

## Où trouver quoi

Le notebook, son export HTML, `recommender.py`, `products_clusters_topics.csv` et `topic_encoded_df.csv` sont dans `07_north_face\the_north_face_project\`.
