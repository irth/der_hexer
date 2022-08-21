from dataclasses import dataclass
from tkinter import W
from typing import List, Optional
from math import sin, cos, pi

HEX_RADIUS: float = 50

HEX_WIDTH: float = 2 * HEX_RADIUS * sin(pi/6)
HEX_HEIGHT: float = 2 * HEX_RADIUS
HEX_SIDE: float = 2 * HEX_RADIUS * sin(pi/6)
EVEN_ROW_OFFSET: float = HEX_WIDTH / 2


@dataclass
class Point:
    x: int
    y: int

    def __sub__(self, point: 'Point') -> 'Point':
        return Point(
            x=self.x - point.x,
            y=self.y - point.y,
        )

    def __add__(self, point: 'Point') -> 'Point':
        return Point(
            x=self.x + point.x,
            y=self.y + point.y,
        )

    def __abs__(self) -> 'Point':
        return Point(x=abs(self.x), y=abs(self.y))

    def __neg__(self) -> 'Point':
        return Point(x=-self.x, y=-self.y)


@dataclass
class HexCoords:
    row: int
    column: int

    @property
    def center(self) -> Point:
        even_row = self.row % 2 == 0
        x_offset = 0 if even_row else EVEN_ROW_OFFSET

        x = x_offset + self.column * HEX_WIDTH
        y = self.row * (HEX_HEIGHT - HEX_SIDE)
        return Point(x, y)

    def in_bounds(self, point: Point) -> bool:
        center = self.center
        point_norm = abs(point - center)

        slope_y = HEX_HEIGHT / 2
        slope_x = HEX_WIDTH
        slope = -slope_y / slope_x

        start_y = HEX_HEIGHT / 2
        top_line = slope * point_norm.x + start_y

        return point_norm.x <= HEX_WIDTH / 2 \
            and point_norm.y <= top_line

    @property
    def polygon(self) -> List[Point]:
        c = HEX_RADIUS * cos(pi/6)
        s = HEX_RADIUS * sin(pi/6)

        A = Point(0, HEX_RADIUS)
        B = Point(c, s)
        C = Point(c, -s)
        D = -A
        E = -B
        F = -C

        center = self.center
        return [center + i for i in [A, B, C, D, E, F]]


@dataclass
class River:
    # are rivers directional? if we want the water to flow then yes, otherwise -
    # normalization of start/end order perhaps is needed
    start: HexCoords
    end: HexCoords


@dataclass
class Road:
    # are roads directional? maybe some normalisation of start/end order would
    # be needed.
    start: HexCoords
    end: HexCoords


COLORS: List[str] = [
    'red'
]


class Map:
    def __init__(self, width: int, height: int, roads: Optional[List[Road]] = None, rivers: Optional[List[River]] = None):
        self.hexes = [[0]*width for row in range(height)]
        self.roads = []
        self.rivers = []
