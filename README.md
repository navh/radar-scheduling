# Radar Schedules

Python implementations of Methods for Multi-function Phased Array Radar Beam Scheduling from various papers.

## Context

This started as some MATLAB code, and `all_methods_one_time.py` is an attempt to re-create this faithfully.

It has since evolved into a way to produce pretty plots of small batches of schedules.

To do more bulk runs, `one_million.py` uses multiprocessing to run through many scenarios and write results out to a .parquet file that can be analyzed or plotted later.


## To recreate paper

1. Install python 3.11.2
1. python -m virtualenv venv
1. source activate ./venv
1. pip install requirements.txt (includes a lot of ipynb nonsense)
1. python src/one_million.py (Takes roughly 4 hrs on my computer)
1. open fla.ipynb
1. run all cells

## To run 8 scenarios

1. Run `generate_eight_scenarios.py`
1. Run `eight_scenarios.py`

