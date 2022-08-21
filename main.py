import itertools
import random
from dataclasses import dataclass
from math import cos, pi, sin
from tkinter import W
from typing import List, Optional, Tuple, Union
import colorsys

from PIL import Image, ImageDraw, ImageColor, ImageFont

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

    def __str__(self) -> str:
        return f'point<{self.x},{self.y}>'

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

    def __eq__(self, point: 'Point') -> bool:
        # accounting for floating point errors
        precision = 7
        threshold = pow(10, -precision)
        return abs(point.x - self.x) < threshold and abs(point.y - self.y) < threshold


@dataclass
class HexCoords:
    row: int
    column: int

    def __str__(self) -> str:
        return f'hex<row={self.row},col={self.column}>'

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


class InvalidRiverException(Exception):
    pass


class River:
    # are rivers directional? if we want the water to flow then yes, otherwise -
    # normalization of start/end order perhaps is needed
    between: Tuple[HexCoords, HexCoords]
    points: List[Point]
    color: int

    def __init__(self, between: Tuple[HexCoords, HexCoords], color: int):
        if len(between) != 2:
            raise InvalidRiverException(
                f'A river is defined by 2 hexagons. {len(between)} were given instead.')
        self.between = between
        self.color = color

        common = list()
        for a, b in itertools.product(between[0].polygon, between[1].polygon):
            if a == b and a not in common:
                common.append(a)
        if len(common) != 2:
            raise InvalidRiverException(
                f'Hexes {between[0]} and {between[1]} do not have a common edge.')

        self.points = list(common)


@dataclass
class Road:
    # are roads directional? maybe some normalisation of start/end order would
    # be needed.
    start: HexCoords
    end: HexCoords
    color: int


COLORS: List[str] = [
    'white',
    'red',
    'blue',
    'green',
    'orange',
    'yellow'
]


def darken(color, amount):
    r, g, b = ImageColor.getrgb(color)

    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    return tuple((int(255 * i) for i in colorsys.hsv_to_rgb(h, s, v * (1 - amount))))


class Map:
    def __init__(self, rows: int, columns: int, roads: Optional[List[Road]] = None, rivers: Optional[List[River]] = None):
        self.hexes = [[0]*columns for row in range(rows)]
        self.roads = roads or []
        self.rivers = rivers or []
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

    def render(self, border=4, road_width=8, river_width=6, margin=10, supersample=4, font_size=18, draw_coords=True):
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

        for river in self.rivers:
            color = darken(COLORS[river.color], 0.3)
            self._line(draw, river.points[0], river.points[1],
                       river_width, river_width, color, supersample, margin)

        for road in self.roads:
            color = darken(COLORS[road.color], 0.5)
            self._line(draw, road.start.center, road.end.center, road_width,
                       road_width, color, supersample, margin)

        if draw_coords:
            font = ImageFont.truetype(
                font='DejaVuSans.ttf', size=supersample*font_size)
            for row in range(self.rows):
                for column in range(self.columns):
                    coords = HexCoords(row, column)
                    center = (supersample * (margin + coords.center)
                              ).integer_tuple

                    draw.text(center, anchor='mm', text=f'r{row}c{column}',
                              fill='white', font=font, stroke_fill='black', stroke_width=supersample * max(18, font_size) // 18)

        resized = im.resize(size.integer_tuple, Image.Resampling.LANCZOS)
        return resized

    def _circle(self, draw: ImageDraw.Draw, center: Tuple[int, int], radius: int, fill, supersample: int):
        draw.ellipse(
            [
                center[0] - supersample * radius,
                center[1] - supersample * radius,
                center[0] + supersample * radius,
                center[1] + supersample * radius,
            ],
            fill=fill)

    def _line(self, draw: ImageDraw.Draw, start: Point, end: Point, width: int, radius: int, fill, supersample: int, margin: Point):
        start = (supersample * (margin + start)).integer_tuple
        end = (supersample * (margin + end)).integer_tuple
        draw.line([start, end], fill=fill, width=supersample * width)
        self._circle(draw, start, radius=radius,
                     fill=fill, supersample=supersample)
        self._circle(draw, end, radius=radius, fill=fill,
                     supersample=supersample)


if __name__ == '__main__':
    m = Map(10, 10)
    for _ in range(5):
        row = random.randrange(0, 10)
        col = random.randrange(0, 10)
        color = random.randrange(len(COLORS) - 1) + 1
        m[HexCoords(row, col)] = color

    road1 = Road(HexCoords(1, 1), HexCoords(2, 1), color=1)
    m.roads.append(road1)
    road2 = Road(HexCoords(2, 1), HexCoords(2, 2), color=2)
    m.roads.append(road2)

    river1 = River((HexCoords(1, 1), HexCoords(2, 1)), color=1)
    m.rivers.append(river1)

    image = m.render()
    image.show()
    # or
    image.save("map.png")
