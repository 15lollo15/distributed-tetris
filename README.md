# distributed-tetris 
A multiplayer distributed version of the classic Tetris game

## ⚠️ WARNING ⚠️
Before run the game start the **nameserver** with:
```
pyro4-ns
```

## Installation
### Poetry
If you have poetry, from terminal enter in the project directory and type:
```
poetry install
```
Now enter in the poetry venv:
```
poetry shell
```
Now you can run the game by type:
```
python .\src\main.py
```
### Without poetry
You must install the following libraries  on your python:
```
pygame-ce = "^2.4.1"
pyro4 = "^4.82"
pygame-gui = "^0.6.10"
```

## Testers
For testing purpose in the repository there are two testing files for **windows** and for **linux** for run ten players