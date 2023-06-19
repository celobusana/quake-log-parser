## GAME LOG ANALYZER

## Installation
- Install python 3
- Create python vevn `python -m venv venv`
- Activate venv `source venv/bin/activate` or `venv\Scripts\activate.bat`
- Install dev requirements `pip install -r requirements_dev.txt`
  
## Code Quality Tools
- Flake8 `flake8`
- Black
- Isort
- Mypy

# Run code quality tools
`cd src`
`black .`
`isort .`
`flake8 .`
`mypy .`
`

### Run
# CLI
- `python src/main.py --log-file=examples/quake_games.log`
- `python src/main.py --log-file=examples/quake_games.log --log-level=DEBUG`

# VS CODE
Use the launch.json file to run the code
