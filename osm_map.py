from __future__ import annotations

import io
import logging
from collections import deque
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

import pygame

import settings


class OSMMapBuilder:
    """Builds and caches the fixed OSM map used by the game."""
    TILE_SIZE = 256

    def __init__(self) -> None:
        """Initializes HTTP session and cache folders."""
        self.logger = logging.getLogger(__name__)
        settings.TILES_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        settings.MAPS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _tile_cache_path(z: int, x: int, y: int) -> Path:
        """Returns cache path for a single tile."""
        return settings.TILES_CACHE_DIR / f"{z}_{x}_{y}.png"

    @staticmethod
    def _map_cache_path(width: int, height: int) -> Path:
        """Returns cache path for the resized map image."""
        return settings.MAPS_CACHE_DIR / f"hormuz_fixed_strip_z7_83_54__84_54_{width}x{height}.png"

    def _download_tile(self, z: int, x: int, y: int) -> bytes | None:
        """Loads a tile from cache or downloads it."""
        path = self._tile_cache_path(z, x, y)
        if path.exists():
            self.logger.info("Tile cache hit z=%s x=%s y=%s", z, x, y)
            return path.read_bytes()

        url = settings.OSM_TILE_URL.format(z=z, x=x, y=y)
        try:
            req = Request(url, headers={"User-Agent": settings.OSM_USER_AGENT})
            with urlopen(req, timeout=8) as response:
                data = response.read()
        except (URLError, HTTPError, TimeoutError):
            self.logger.warning("Tile download failed z=%s x=%s y=%s", z, x, y)
            return None

        path.write_bytes(data)
        self.logger.info("Tile downloaded z=%s x=%s y=%s", z, x, y)
        return data

    def _load_tile_surface(self, z: int, x: int, y: int) -> pygame.Surface | None:
        """Converts tile bytes to a pygame surface."""
        data = self._download_tile(z, x, y)
        if not data:
            return None
        try:
            return pygame.image.load(io.BytesIO(data)).convert()
        except pygame.error:
            return None

    def _fallback_tile(self) -> pygame.Surface:
        """Builds a simple fallback tile if download fails."""
        tile = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
        tile.fill((195, 211, 216))
        pygame.draw.rect(tile, (213, 204, 183), (0, 0, self.TILE_SIZE, self.TILE_SIZE // 2))
        pygame.draw.line(tile, (120, 132, 141), (0, self.TILE_SIZE // 2), (self.TILE_SIZE, self.TILE_SIZE // 2), 2)
        return tile

    def _compose_fixed_strip(self, width: int, height: int) -> pygame.Surface:
        """Composes the 2 fixed tiles and scales to board size."""
        strip = pygame.Surface((self.TILE_SIZE * 2, self.TILE_SIZE))
        for idx, (z, x, y) in enumerate(settings.OSM_FIXED_BASE_TILES):
            tile = self._load_tile_surface(z, x, y) or self._fallback_tile()
            strip.blit(tile, (idx * self.TILE_SIZE, 0))
        return pygame.transform.smoothscale(strip, (width, height))

    def get_or_build_map(self, width: int, height: int, zoom: int | None = None) -> pygame.Surface:
        """Returns cached map or builds it from the fixed tiles."""
        del zoom  # not used in fixed 2-tile mode
        path = self._map_cache_path(width, height)

        if settings.LOCAL_MAP_ASSET.exists():
            try:
                self.logger.info("Using local bundled map asset: %s", settings.LOCAL_MAP_ASSET)
                bundled = pygame.image.load(str(settings.LOCAL_MAP_ASSET)).convert()
                if bundled.get_size() != (width, height):
                    bundled = pygame.transform.smoothscale(bundled, (width, height))
                return bundled
            except pygame.error:
                self.logger.warning("Local bundled map is invalid: %s", settings.LOCAL_MAP_ASSET)

        if path.exists():
            try:
                self.logger.info("Map cache hit: %s", path)
                return pygame.image.load(str(path)).convert()
            except pygame.error:
                self.logger.warning("Corrupted cached map, rebuilding: %s", path)

        out = self._compose_fixed_strip(width, height)
        pygame.image.save(out, str(path))
        self.logger.info("Map generated from fixed 2-tile strip: %s", path)
        return out

    def build_water_playable_mask(self, map_surface: pygame.Surface, rows: int, cols: int) -> list[list[bool]]:
        """Builds a playable mask by detecting water-colored cells."""
        cell_w = map_surface.get_width() / cols
        cell_h = map_surface.get_height() / rows

        mask = [[False for _ in range(cols)] for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                sx = int((c + 0.5) * cell_w)
                sy = int((r + 0.5) * cell_h)
                sx = max(0, min(map_surface.get_width() - 1, sx))
                sy = max(0, min(map_surface.get_height() - 1, sy))
                red, green, blue, *_ = map_surface.get_at((sx, sy))
                mask[r][c] = blue >= 120 and blue - red >= 14 and blue - green >= 6

        return self._largest_connected_component(mask)

    def _largest_connected_component(self, mask: list[list[bool]]) -> list[list[bool]]:
        """Keeps only the largest connected playable region."""
        rows = len(mask)
        cols = len(mask[0]) if rows else 0
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        best: list[tuple[int, int]] = []

        for r in range(rows):
            for c in range(cols):
                if visited[r][c] or not mask[r][c]:
                    continue
                comp: list[tuple[int, int]] = []
                q = deque([(r, c)])
                visited[r][c] = True
                while q:
                    cr, cc = q.popleft()
                    comp.append((cr, cc))
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr = cr + dr
                            nc = cc + dc
                            if nr < 0 or nr >= rows or nc < 0 or nc >= cols:
                                continue
                            if visited[nr][nc] or not mask[nr][nc]:
                                continue
                            visited[nr][nc] = True
                            q.append((nr, nc))
                if len(comp) > len(best):
                    best = comp

        if not best:
            return [[True for _ in range(cols)] for _ in range(rows)]

        out = [[False for _ in range(cols)] for _ in range(rows)]
        for r, c in best:
            out[r][c] = True
        return out
