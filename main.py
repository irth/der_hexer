import random
from dataclasses import dataclass
from math import cos, pi, sin
from tkinter import W
from typing import List, Optional, Tuple, Union

from PIL import Image, ImageDraw

HEX_RADIUS: float = 50

HEX_WIDTH: float = 2 * HEX_RADIUS * cos(pi/6)
HEX_HEIGHT: float = 2 * HEX_RADIUS
HEX_SIDE: float = 2 * HEX_RADIUS * sin(pi/6)
ROW_OVERLAP: float = HEX_RADIUS * (1 - sin(pi/6))
EVEN_ROW_OFFSET: float = HEX_WIDTH / 2


@dataclass
class Point:
    x: float
    y: float

    @property
    def tuple(self) -> Tuple[(float, float)]:
        return (self.x, self.y)

    @property
    def integer_tuple(self) -> Tuple[(int, int)]:
        # does weirdness of python's round matter?
        return (round(self.x), round(self.y))

    def __sub__(self, point: 'Point') -> 'Point':
        return Point(
            x=self.x - point.x,
            y=self.y - point.y,
        )

    def __mul__(self, scale: Union[float, int]) -> 'Point':
        return Point(x=scale * self.x, y=scale * self.y)

    def __rmul__(self, scale: Union[float, int]) -> 'Point':
        return Point(x=scale * self.x, y=scale * self.y)

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
        row_offset = 0 if even_row else EVEN_ROW_OFFSET
        offset = Point(
            x=row_offset + HEX_WIDTH / 2,
            y=HEX_HEIGHT / 2
        )

        return offset + Point(
            x=self.column * HEX_WIDTH,
            y=self.row * (HEX_HEIGHT - ROW_OVERLAP)
        )

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
    'white',
    'red',
    'blue',
    'green',
    'orange',
    'yellow'
]


class Map:
    def __init__(self, rows: int, columns: int, roads: Optional[List[Road]] = None, rivers: Optional[List[River]] = None):
        self.hexes = [[0]*columns for row in range(rows)]
        self.roads = []
        self.rivers = []
        self.columns = columns
        self.rows = rows
        self.image_size = Point(
            x=HEX_WIDTH * columns + EVEN_ROW_OFFSET,
            y=(HEX_HEIGHT - ROW_OVERLAP) * rows + ROW_OVERLAP,
        )

    def __getitem__(self, coords: HexCoords) -> int:
        return self.hexes[coords.row][coords.column]

    def __setitem__(self, coords: HexCoords, value: int):
        self.hexes[coords.row][coords.column] = value

    def render(self, border=4, margin=10, supersample=4):
        margin = Point(margin + border, margin + border)
        size = (2 * margin + self.image_size)
        im = Image.new(
            "RGB",
            (supersample * size).integer_tuple,
            color="black"
        )
        draw = ImageDraw.Draw(im, "RGB")

        for row in range(self.rows):
            for column in range(self.columns):
                coords = HexCoords(row, column)
                value = self[coords]
                color = COLORS[value]

                draw.polygon([(supersample * (margin + p)).tuple for p in coords.polygon],
                             fill=color, outline="black", width=(supersample * border) // 2)
        resized = im.resize(size.integer_tuple, Image.ANTIALIAS)
        return resized


if __name__ == '__main__':
    m = Map(10, 10)
    for _ in range(5):
        row = random.randrange(0, 10)
        col = random.randrange(0, 10)
        color = random.randrange(len(COLORS) - 1) + 1
        m[HexCoords(row, col)] = color
    image = m.render()
    image.show()
    # or
    image.save("map.png")
