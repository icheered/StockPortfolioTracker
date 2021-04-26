# PortfolioTracker Service
This program takes a list of transactions in CSV format (exported from DeGiro) and calculates the portfolio's performance over time. 

Also contains a script for updating the information which can be run daily through CRON or similar service

## Installation
This backend uses Poetry for dependency management. Poetry can be installed using your system's package manager but it is recommended to use [the official install script](https://python-poetry.org/docs/#installation).

```bash
# Initiate virtual environment
$ poetry shell

# Install the dependencies
$ poetry install
```

Copy/rename the `config.ini.dist` file to `config.ini` and fill out your parameters.

Make sure you have a RethinkDB docker container running
```
$ docker run -d -p 8085:8080 -p 28015:28015 -p 29015:29015 -P --name rethink1 rethinkdb
```

```
# Run the program
$ python main.py
```