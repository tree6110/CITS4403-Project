# Housing market model

## Description
This project provides an agent-based model of the Perth housing market.
Agents can buy and sell property, move in and out of houses, and interact with banks.
At each step, a visualization of the housing grid with information regarding income distribution, housing ownership distribution and other relevant statistics is produced.

## Prerequisites
Install `uv` according to the docs [here](https://docs.astral.sh/uv/getting-started/installation/).
## Running the model
After making sure you have `uv` installed, navigate to `housingSimulator/src` and run the model with the following commands:
```
cd housingSimulator/src
uv run model.py
```
Please note that the model must be run from the `src` directory.
The model may take some time to complete. By default, 20 ticks will be computed, with output produced in the `housingSimulator/src/results` directory. The number of steps computed can be altered by changing the number in the call to `runSimulation()` in `main.py`.
