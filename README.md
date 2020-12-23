# QTSP - a quantum TSP demo

This repository contains a demo comparing classic and quantum versions of the Traveling Salesperson Problem using the D-Wave Ocean SDK. This demo takes an input CSV containing geocoordinates for cities to be visited, builds a graph with approximate distances between them using the Haversine formula, and then tries to find the route with the minimum distance to visit each city once.

## Setup

To get started, follow these steps:

1. Create a D-Wave Leap account. You can do so here: https://cloud.dwavesys.com/leap/.
2. Install the D-Wave Ocean SDK.  To do so, run:
```
    pip install dwave-ocean-sdk
```
3. Set up the D-Wave Ocean environment. To do so, run:
```
    dwave setup
```
Then follow the prompts. You will install some additional packages, accept a EULA, and enter some SDK configuration values, including an API endpoint URL and authentication token, which you can find in the D-Wave Leap console.

## Usage

To execute the program, enter the `src` directory and run:

    python main.py <version>

Where \<version> takes one of three values:

- classic: runs a classic, exhaustive search TSP algorithm to find the best route.
- hybrid: uses the D-Wave NetworkX library implementation of TSP and runs it using the Leap Hybrid sampler.
- quantum: uses a modified version of the D-Wave NetworkX library implementation of TSP that makes the Lagrange parameter more explicit and estimates a "weight factor" to improve the accuracy of the algorithm. The Lagrange parameter is the "A" value and the "weight factor" is the "B" value in the TSP formula give in [this paper](https://arxiv.org/pdf/1302.5843.pdf). This runs on the Leap Hybrid sampler.

The program is currently hard-coded to use `data/test-data.csv` as the input file. You can update or replace this file to use your data or update main.py to use a different input file.