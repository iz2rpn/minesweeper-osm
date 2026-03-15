# Minesweeper OSM (Desktop)

Python + Pygame desktop game.

## Run from source
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Build with PyInstaller

Install:
```bash
pip install pyinstaller
```

Build (Windows):
```bash
pyinstaller --noconfirm --onefile --name MinesweeperOSM --add-data "assets;assets" main.py
```

Build (Linux/macOS):
```bash
pyinstaller --noconfirm --onefile --name MinesweeperOSM --add-data "assets:assets" main.py
```

Output executable:
- `dist/MinesweeperOSM(.exe)`

## Runtime folders
- `assets/` are loaded from the app bundle.
- `cache/` and `logs/` are created in the folder where you launch the app.

All characters and events in this work are fictional. Any resemblance to real persons or events is purely coincidental.