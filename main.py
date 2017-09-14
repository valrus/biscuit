"""
"""
import os

import kivy
kivy.require("1.5.0")

from kivy.animation import Animation
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import ListProperty, ReferenceListProperty, NumericProperty, StringProperty
from math import sin, pi

import itertools
import random

SIN60 = sin(pi / 3.0)
SLOPE = (2.0 / 3.0) * SIN60
SCALE = dp(20.0)
THICKNESS = 2
HEX_VERTICES = ([SIN60, 0], [2 * SIN60, 0.5],
                [2 * SIN60, 1.5], [SIN60, 2.0],
                [0, 1.5], [0, 0.5])


def hex_to_pos(hex_x, hex_y):
    return SCALE * (hex_x * 2.0 + (hex_y % 2)) * SIN60, SCALE * 1.5 * hex_y


class Letter(Button):
    text = StringProperty("@")

    def on_parent(self, widget, parent):
        self.size = parent.size


class Player(object):
    def __init__(self, hex_x, hex_y, **kw):
        super(Player, self).__init__()
        self.x, self.y = hex_x, hex_y
        self.widget = Letter(pos=hex_to_pos(hex_x, hex_y))


class Tile(AnchorLayout):
    r = NumericProperty(1.0)
    g = NumericProperty(1.0)
    b = NumericProperty(1.0)
    a = NumericProperty(1.0)
    fillColor = ReferenceListProperty(r, g, b, a)
    vertices = ListProperty([])

    def vertices(self):
        return [[SCALE * x + self.x, SCALE * y + self.y] for (x, y) in HEX_VERTICES]

    def __init__(self, hex_x, hex_y, scale=SCALE):
        self.hex_x, self.hex_y = hex_x, hex_y
        self.scale = scale
        self.pos = hex_to_pos(hex_x, hex_y)
        xyuv = [v + [0, 0] for v in self.vertices()]
        self.vertices = list(itertools.chain(*xyuv))
        super(Tile, self).__init__(
            size=(2 * SIN60 * self.scale, 2.0 * self.scale)
        )

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        self.g, self.b = 0.0, 0.0
        Animation(r=0.0).start(self)
        Animation(b=1.0).start(self)
        print("Touch widget at ({0}, {1})".format(self.hex_x, self.hex_y))
        print("Widget vertices: ", self.vertices)
        print("Widget position: ", self.pos)
        return False

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            return self.on_touch_down(touch)
        return False

    def collide_point(self, *point):
        if not super(Tile, self).collide_point(*point):
            return False
        rel_x, rel_y = self.to_local(*point, relative=True)
        dy = SLOPE * rel_x
        if rel_x <= SIN60 * self.scale:
            y_min, y_max = (self.scale * 0.5) - dy, (self.scale * 1.5) + dy
        else:
            y_min, y_max = dy - (self.scale * 0.5), (self.scale * 2.5) - dy
        return y_min < rel_y < y_max

    def letter_clicked(self, label):
        print("Click on {}".format(label))


class Biscuit(App):
    def build(self):
        root = RelativeLayout(pos=(SCALE / 2, SCALE / 2))
        widgetArray = []
        for x in range(0, 22):
            widgetArray.append([])
            for y in range(0, 19):
                widgetArray[x].append(Tile(x, y))
                root.add_widget(widgetArray[x][y])
        player_x, player_y = random.randrange(0, 22), random.randrange(0, 19)
        player_tile = widgetArray[player_x][player_y]
        player = Player(player_x, player_y,
                        anchor_x="center", anchor_y="center",
                        text_size=(None, None))
        player_tile.add_widget(player.widget)
        player_tile.r = 0.0
        print("Player location: ({0}, {1})".format(player_x, player_y))
        print("Player position: ({0}, {1})".format(player.widget.x,
                                                   player.widget.y))
        print(player.widget.parent)
        return root

if __name__ == '__main__':
    Biscuit().run()
