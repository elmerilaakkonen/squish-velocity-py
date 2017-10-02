# Two-stroke engine squish velocity calculator

Based on G.P. Blair's method presented in the book "Design and Simulation of Two-Stroke Engines".
Implemented in [Python](https://www.python.org/) using [Tk](https://docs.python.org/3/library/tk.html) and [Matplotlib](http://matplotlib.org/).

Works with non-negative squish angles only (angle>=0°).

## Installation
1. Make sure you have [Python3](https://www.python.org/downloads/) installed.
2. Clone directory (you need squish_velocity.py and data.txt)
3. Run `pip3 install matplotlib`
4. Run `python squish_velocity.py` at the dir containing the files

## Usage
Input numerical values for engine parameters. Program tries to fetch values from *data.txt* if available.
The program saves values to *data.txt* automatically when "Calculate" is clicked for ease of use.

### License
Licensed under GPLv3.
