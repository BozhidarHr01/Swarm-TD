import pygame
from os.path import join
from os import walk

WINDOW_WIDTH, WINDOW_HEIGHT = 1600, 900
TILE_SIZE = 16

ROOM_COUNT = 50

# scale camera
CAMERA_WIDTH = WINDOW_WIDTH // 2   # 2x zoom
CAMERA_HEIGHT = WINDOW_HEIGHT // 2
CAMERA_ZOOM = 1.25 