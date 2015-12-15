# schneiderman
Predictive analytics for daily fantasy basketball.

# Installation

`pip install -r requirements.txt`

# Project Structure

## Code

- `sources/` The data sources for the analytics.
- `scrape/` Various data scrapers.

## Data

- `static` Static data, one time fetch.

# Scrape

The `scrape` directory contains a API resource implementation for the NBA stats
undocumented API.  We implement:

- NbaPlayerList
- NbaPlayerGameLog
- NbaTeamList
- NbaTeamInfo
