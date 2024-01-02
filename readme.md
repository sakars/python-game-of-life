# Game of life in python with C optimizations

![GitHub top language](https://img.shields.io/github/languages/top/sakars/python-game-of-life)

This project contains a Python project that is able to simulate Conway's game of life.

Simulation controls:
- P - toggle pause
- . (period) - Speed up simulation
- , (comma) - Slow down simulation
- Space - step once (useful when simulation is paused)
- Escape - quit

You can load RLE files containing conway's game of life patterns. [Site for popular patterns.](https://conwaylife.com/wiki/)

You can also create your own patterns.
Creation controls:
- Left click - Place living cells
- Right click - Place dead cells
- R - preview current configuration
- Escape - quit

Closing the pattern maker opens a prompt to save it as an RLE file.