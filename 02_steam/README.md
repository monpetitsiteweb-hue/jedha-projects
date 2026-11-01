# Steam videogames platform: market analysis for Ubisoft (Jedha, Big Data project)

Ubisoft wants to release a new game and asked for a global analysis of the games available on Steam: what the market looks like and which factors go together with popular games.

The analysis is done on **Databricks with PySpark** on the Steam catalogue (`s3://full-stack-bigdata-datasets/Big_Data/Project_Steam/steam_game_output.json`, about 55,000 games, nested JSON). Charts are built with the **Databricks visualization tool**.

## Notebooks

| Notebook | Content |
|---|---|
| `setup_data` | Shared loading and cleaning, run by every notebook with `%run ./setup_data` (no table or chart on purpose) |
| `00_data_exploration` | Raw schema, data quality checks, validation of the cleaning |
| `01_macro_analysis` | Publishers, best rated games, releases per year and Covid, prices and discounts, languages, age restrictions |
| `02_genres_analysis` | Most represented genres, review ratio by genre, publishers' favourite genres, most lucrative genres, community tags |
| `03_platforms_and_popularity` | Windows / Mac / Linux availability, genre x platform, factors associated with popular games |

A summary in French is in `SYNTHESE.md`.

## Notebook outputs

Databricks no longer offers notebook publishing, so the cell outputs are delivered as exports and screenshots. `00_data_exploration` was run on October 31, 2026, and `01`, `02` and `03` on November 1, 2026.

| Location | Content |
|---|---|
| `notebooks/` | `00` to `03` with their saved outputs; `setup_data` displays no table or chart on purpose |
| `captures/*.html` | Full Databricks exports of the 5 notebooks, charts included (an internet connection is needed to display them) |
| `captures/*.ipynb` | The same exports in notebook format |
| `captures/*.png` | 22 screenshots of cell outputs, listed in [`captures/LISTE-CAPTURES.md`](captures/LISTE-CAPTURES.md) |

## Methodology highlights

- Nested schema flattened with `select("data.*")`; genres, languages, platforms and tags exploded into dedicated dataframes (`explode`, `split`, `from_json` to turn the tags struct into a map).
- Robust parsing with `try_cast` / `try_to_timestamp` (Spark 4 and serverless compute run in ANSI mode, where a plain cast fails on a malformed value).
- Ratings ranked with the **Wilson lower bound** of the positive review ratio, so that a game with 3 positive reviews does not beat a game with 50,000 reviews at 97%.
- Popularity proxies: **estimated owners** (SteamSpy range midpoint) and **number of reviews**. Estimated revenue = owners x current price, an order of magnitude only (no sales data, discounts and regional prices ignored).
- Notebooks `01`, `02` and `03` each have a "Key figures" cell computed from the data; `03` continues with reading notes.

## Run it

1. In Databricks: **Workspace > (your folder) > Import**, import the 5 `.ipynb` files of `notebooks/` into the **same folder** (`%run ./setup_data` needs it).
2. Attach serverless compute (or a cluster) and **Run all** on `00_data_exploration`, then `01`, `02`, `03`.
3. If the S3 bucket cannot be read from the workspace, follow the fallback comment in the first code cell of `setup_data` (upload the JSON to a Unity Catalog volume).
