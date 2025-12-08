import pygame
from os.path import join
from os import walk

WINDOW_WIDTH, WINDOW_HEIGHT = 1530, 950
TILE_SIZE = 16

ROOM_COUNT = 5

# scale camera
CAMERA_WIDTH = WINDOW_WIDTH // 2   # 2x zoom
CAMERA_HEIGHT = WINDOW_HEIGHT // 2
CAMERA_ZOOM = 1.2

ENEMY_HEALTH = 5
FLYING_ENEMY_HEALTH = 3
ENEMY_DAMAGE = 1
PLAYER_DAMAGE = 1
PLAYER_HEALTH = 5
PLAYER_FIRE_RATE = 400
PLAYER_SPEED = 200
BOMB_DAMAGE = 15

WIRE_SLOW_FACTOR = 0.2

#skeleton: 
SKELETON_SHOOT_PAUSE = 500
SKELETON_ATTACK_COOLDOWN = 2000
SKELETON_BONE_LIFETIME = 1000

MAX_ENEMY_COUNT = 30
ENEMY_DESPAWN_TIME = 20000 # ms
ENEMY_SPEED = 100
ENEMY_SPAWN_INTERVAL = 300

#BOSS
BOSS_HEALTH = 500
BOSS_SPEED = 60
BOSS_DAMAGE = 1
BOSS_ROCK_DAMAGE = BOSS_DAMAGE * 2

SMASH_RANGE = 300 # pixels
SMASH_ANGLE = 70 # degrees
SMASH_DAMAGE = BOSS_DAMAGE * 2
SMASH_COOLDOWN = 6000 # 6s

MAX_TURRET_COUNT = 5
TURRET_LIFETIME = 30000
TURRET_FIRE_RATE = 0.5
TURRET_FIRE_INTERVAL = 100
TURRET_RANGE = 300
TURRET_DAMAGE = 1

BULLET_LIFETIME = 1000
BULLET_SPEED = 350

TRAP_DAMAGE = 5
TRAP_ANIMATION_SPEED = 0.25
TRAP_ANIMATION_TIME = 0

# money 
STARTING_MONEY = 150
TURRET_COST = 50
WALL_COST = 30
TRAP_COST = 35
BARBED_WIRE_COST = 25
ENEMY_KILL_MONEY_REWARD = 5
BOMB_COST = 25

# upgrades
UPGRADE_SIZE = 30
UPGRADES = [
    {'name': 'Heal', 'weight': 20, 'image': join('images', 'upgrades', 'heal.png')},
    {'name': 'HealthUp', 'weight': 10, 'image': join('images', 'upgrades', 'healthup.png')},
    {'name': 'Damage', 'weight': 15, 'image': join('images', 'upgrades', 'damage.png')},
    {'name': 'Money', 'weight': 20, 'image': join('images', 'upgrades', 'money.png')},
    {'name': 'FireRate', 'weight': 15, 'image': join('images', 'upgrades', 'firerate.png')},
    {'name': 'Speed', 'weight': 13, 'image': join('images', 'upgrades', 'speed.png')},
    {'name': 'Range', 'weight': 13, 'image': join('images', 'upgrades', 'range.png')},
]

DAMAGE_UPGRADE = 1
MONEY_UPGRADE = 50
SPEED_UPGRADE = 15
RANGE_UPGRADE = 125

# custom font
FONT_PATH = join('font', 'ScienceGothic.ttf')

# room placement
ROOMS_DIR = join('maps', 'tsx', 'tboi')
END_ROOMS_DIR = join('maps', 'tsx', 'tboi', 'deadend')
DOOR_SIZE = 64

MIN_ENEMY_COUNT = 1
MAX_ENEMY_COUNT = 3

LOOT_DROP_CHANCE = 0.5