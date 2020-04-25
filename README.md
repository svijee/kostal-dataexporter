# Kostal Piko Dataexporter

This Python scripts grabs content of the REST API of a [Kostal PIKO
7.0](https://www.kostal-solar-electric.com/de-de/products/three-phase-inverter/piko-12-20)
and exports the data to a PostgreSQL Database.

## Setup

 * Import the `init.sql` into your PostgreSQL Database
 * Set environment variables with the relevant details
  * `KOSTAL_USERNAME`
  * `KOSTAL_PASSWORD`
  * `KOSTAL_HOST`
  * `DB_HOST`
  * `DB_PORT`
  * `DB_NAME`
  * `DB_USER`
  * `DB_PASSWORD`
 * Run `python kostal-piko-dataexport.py`

There's also a Docker Image available on [Docker Hub](https://hub.docker.com/r/svijee/kostal-dataexporter).

## Grafana

By logging the data with this script it's easily possible to create a nice
Grafana Dashboard to display some of the interesting data:

![My dashboard on a sunny day in Germany](https://raw.githubusercontent.com/svijee/kostal-dataexporter/master/img/grafana-dashboard.png)

You can import the [dashboard.json](dashboard.json) to use it in your Grafana
instance.

## Note

This is just a quick-and-dirty script to grab to content of the REST-API of my
Kostal Piko 7.0 Inverter. This might be usable on other Inverters aswell.
