import sys
from pathlib import Path


# Gameplay
BOARD_COLS = 30
BOARD_ROWS = 16
MINE_COUNT = 99
CELL_SIZE = 28  # 24-32 px
HUD_HEIGHT = 84  # 70-90 px
BORDER = 10
FPS = 60

# OSM area (Strait of Hormuz)
OSM_NORTH = 27.25
OSM_SOUTH = 26.15
OSM_WEST = 55.20
OSM_EAST = 56.95
OSM_CENTER_LAT = 26.73
OSM_CENTER_LON = 56.10
OSM_ZOOM = 9
OSM_USER_AGENT = "HormuzMinesweeper/1.0 (+local desktop app)"
OSM_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
OSM_FIXED_BASE_TILES = ((7, 83, 54), (7, 84, 54))
OSM_USE_FIXED_TILE_STRIP = True

# Paths
ROOT_DIR = Path(__file__).resolve().parent
BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", ROOT_DIR))
RUNTIME_DIR = Path.cwd()

ASSETS_DIR = BUNDLE_DIR / "assets"
CACHE_DIR = RUNTIME_DIR / "cache"
TILES_CACHE_DIR = CACHE_DIR / "tiles"
MAPS_CACHE_DIR = CACHE_DIR / "maps"
LOG_DIR = RUNTIME_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"
LOCAL_MAP_ASSET = ASSETS_DIR / "hormuz_fixed_strip_840x448.png"

# Colors
WINDOW_BG = (41, 47, 58)
FRAME_LIGHT = (150, 158, 170)
FRAME_DARK = (85, 93, 106)
HUD_BG = (66, 74, 88)
HUD_INNER = (57, 65, 78)
COUNTER_BG = (16, 8, 8)
COUNTER_RED = (212, 20, 16)

COVERED_BASE = (196, 202, 210)
COVERED_LIGHT = (231, 236, 242)
COVERED_DARK = (125, 134, 146)
REVEALED_OVERLAY = (240, 242, 239, 92)
REVEALED_BORDER = (104, 114, 124)
GRID_LINE = (68, 81, 94, 110)
COVERED_ALPHA = 108

MINE_COLOR = (43, 53, 63)
MINE_RING = (20, 28, 36)
MINE_EXPLODED_BG = (194, 98, 92)
WRONG_FLAG_BG = (223, 186, 116)
FLAG_RED = (176, 21, 26)
FLAG_DARK = (30, 41, 52)
QUESTION_COLOR = (78, 86, 97)

NUMBER_COLORS = {
    1: (33, 66, 197),
    2: (33, 130, 49),
    3: (179, 30, 25),
    4: (24, 43, 136),
    5: (118, 32, 28),
    6: (22, 121, 129),
    7: (26, 26, 26),
    8: (98, 98, 98),
}
