# NBA DFS Dashboard

A react app to display various NBA DFS tools and a python flask backend to serve data through a json api.

## Motivation

Playing NBA DFS well requires me to keep up to date with how players have been doing in recent games and how players are doing right before the game slate starts. Having tools to not only scrape the data but to visualize and interact the data in a clean simple way is extremely helpful for getting the most value out of the data.

I've been able to scrape data easily using my [other tool](https://github.com/jsonchin/nba_stats_scraper_db_storage) and have been using that data to create a model to predict a player's performance each night. While having a model and optimizer that produces lineups is nice, understanding and having confidence in those lineups by easily looking up past performance or today's injuries make it even better.

## Goals/Features

- A tool to look up past game box scores and lookup past player logs without having to open a new tab or new page
- A tool to look at lineups and past injuries and once again lookup past player logs or box scores without having to open a new page

## Instructions

1) Setup and install the needed python and npm packages
```
make setup
```

2) Configure the database path and name in `nba_dashboard/config.py` which uses tables create from scrape jobs located in `api_requests.yaml`.

3) Run the app
```
make run
```
and open the app on `http://127.0.0.1:5000/`
