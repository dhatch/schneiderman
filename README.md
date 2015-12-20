# schneiderman
Predictive analytics for daily fantasy basketball.

# Installation

`pip install -r requirements.txt`

# Project Structure

## Executables

## Code

The python code is contained within the `schneiderman` module.

Any executable files (python or otherwise) are within `bin/`.

### `schneiderman/`:

- `scrape/` Various data scrapers.
- `models/` Persistent storage for scraped and processed data.
- `regresssion/` The linear modeling tools used on the gathered data to predict weekly scores.
- `lineup/` Randomized algorithm used in generating lineups from predicted weekly scores.

## Data

- `static` Static data.  Supports analysis, changes infrequently, fetched manually.
- `data/` The user local data folder.  Used for temporary storage of pipeline
  stage data.  *Ignored* by git.
    - `data/clean` Output data from `bin/clean`.
    - `data/scrape` Output data from `bin/scrape`
    - `data/games` Output data from `bin/load_games`
    - `data/train` Output data from `bin/train`
    - `data/predict` Output data from `bin/predict`
    - `data/lineup` Output data from `bin/lineups`
