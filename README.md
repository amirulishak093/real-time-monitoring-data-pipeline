# Real-Time Monitoring Data Pipeline

This repository contains a real-time monitoring data pipeline designed to process and analyze data streams in real-time, leveraging Telegraf, InfluxDB, and Grafana.

## Table of Contents

- [Real-Time Monitoring Data Pipeline](#real-time-monitoring-data-pipeline)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Components](#components)
  - [Getting Started](#getting-started)

## Overview

The real-time monitoring data pipeline uses data streams provided by a Flask app through API endpoints that simulate readings from sensor data. The metric data is collected using Telegraf at an interval of 5 seconds and flushed to the target source InfluxDB at an interval of 5 seconds.

## Components

The real-time monitoring data pipeline consists of following components:

- <b>Flask App:</b> Provides API endpoints to simluate readings from sensor data.
- <b>Telegraf:</b> Collects metric data from the Flask app at 5-second interval.
- <b>InfluxDB:</b> Stores the collected metric data.
- <b>Grafana:</b> Visualizes and analyzes real-time data from InfluxDB.

## Getting Started

To use the real-time monitoring data pipeline, follow these steps:

1. Copy the `.env.example` file to `.env`
2. Configure the environment variables in the .env file according to your setup.
3. Start the Docker containers: `docker compose up -d`
4. The Flask app endpoints can be accessed at `http//:127.0.0.1:2800`
5. To access protected endpoints, you need to include the access token in the request header as Authorization.
   Example:
   ````console
    GET /sensor-data?zone_name=lab HTTP/1.1
    Host: 127.0.0.1:2800
    Authorization: <access_token>```
   ````
6. Open Grafana on your browser: `http://127.0.0.1:3000`
7. Configure Grafana to connect to InfluxDB as data source.
8. Create dashboards in Grafana to visualize and analuze the real-time data.
