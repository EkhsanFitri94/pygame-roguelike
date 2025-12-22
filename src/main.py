# src/main.py

import pygame
import random
import sys
import os

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
TILESIZE = 32

# Map dimensions
MAP_WIDTH = SCREEN_WIDTH // TILESIZE
MAP_HEIGHT = SCREEN_HEIGHT // TILESIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 150, 0)
PLAYER_COLOR = (255, 0, 255) # NEW: A distinct color for the player

# Tiles
TILE_WALL = 0
TILE_FLOOR = 1

# --- Classes ---

# NEW: The Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        # Use a Vector2 for position for easier math
        self.pos = pygame.math.Vector2(x * TILESIZE, y * TILESIZE)
        self.vel = pygame.math.Vector2(0, 0)

    def update(self):
        # Handle player input
        self.vel = pygame.math.Vector2(0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -4
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = 4
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vel.y = -4
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vel.y = 4

        # Move the player based on velocity
        self.pos += self.vel

    def draw(self, screen, camera_offset):
        # Draw the player relative to the camera
        draw_rect = self.rect.copy()
        draw_rect.topleft = (self.pos.x - camera_offset[0], self.pos.y - camera_offset[1])
        screen.blit(self.image, draw_rect)

# --- Functions ---
def generate_dungeon():
    """Generates a dungeon using a random walk algorithm."""
    print("--- generate_dungeon function has been called ---")
    
    # Start with a map full of walls
    dungeon_map = [[TILE_WALL for _ in range(MAP_HEIGHT)] for _ in range(MAP_WIDTH)]
    
    # Random walk settings
    total_tiles = MAP_WIDTH * MAP_HEIGHT
    target_floor_tiles = total_tiles // 2  # Aim for 50% floor tiles
    current_floor_tiles = 0
    
    # Starting position for walk
    walker_x = random.randrange(1, MAP_WIDTH - 1)
    walker_y = random.randrange(1, MAP_HEIGHT - 1)
    dungeon_map[walker_x][walker_y] = TILE_FLOOR
    current_floor_tiles += 1
    
    # The random walk
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W
    while current_floor_tiles < target_floor_tiles:
        # Pick a random direction
        dx, dy = random.choice(directions)
        
        # Calculate new position for walker
        new_walker_x = walker_x + dx
        new_walker_y = walker_y + dy
        
        # --- Robust Boundary Check ---
        # Check if the new position is within valid map boundaries.
        is_x_valid = 1 <= new_walker_x <= MAP_WIDTH - 2
        is_y_valid = 1 <= new_walker_y <= MAP_HEIGHT - 2
        
        if is_x_valid and is_y_valid:
            # The walker's position is valid. Update the walker's position.
            walker_x, walker_y = new_walker_x, new_walker_y
            
            # Now, access the map using the VALIDATED coordinates.
            # This will always work, regardless of variable names.
            if dungeon_map[walker_x][walker_y] == TILE_WALL:
                dungeon_map[walker_x][walker_y] = TILE_FLOOR
                current_floor_tiles += 1
                
    return dungeon_map

def draw_map(screen, dungeon_map):
    """Draws the dungeon map to the screen."""
    for x, column in enumerate(dungeon_map):
        for y, tile in enumerate(column):
            if tile == TILE_WALL:
                color = DARK_GREEN
            elif tile == TILE_FLOOR:
                color = GREEN
            else:
                color = BLACK  # Should not happen
            
            rect = pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
            pygame.draw.rect(screen, color, rect)

# --- Game Class (to hold everything) ---
class Game:
    def __init__(self):
        # Initialize pygame and create window
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike")
        self.clock = pygame.time.Clock()
        self.running = True

    def new(self):
        # Start a new game
        self.all_sprites = pygame.sprite.Group()
        
        # Generate the dungeon
        self.dungeon_map = generate_dungeon()
        
        # NEW: Create the player instance
        # Place player in the center of the first floor tile found
        player_start_pos = None
        for y, row in enumerate(self.dungeon_map):
            for x, tile in enumerate(row):
                if tile == TILE_FLOOR and player_start_pos is None:
                    player_start_pos = (x, y)
                    break # Found the first floor tile, no need to keep looking
            if player_start_pos is not None:
                break
        
        if player_start_pos:
            self.player = Player(self, player_start_pos[0], player_start_pos[1])
        else:
            # Fallback: place player at 10, 10 if no floor is found (shouldn't happen)
            self.player = Player(self, 10, 10)
            
        self.all_sprites.add(self.player)
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(30)

            # Handle Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playing = False
                    self.running = False

            # Update
            self.player.update()

            # Draw
            self.screen.fill(BLACK)
            draw_map(self.screen, self.dungeon_map)
            
            # NEW: Draw the player
            self.player.draw(self.screen, (0, 0)) # Camera offset is (0,0) for now
            
            pygame.display.flip()

# --- Main Game Loop ---
g = Game()
while g.running:
    g.new()

pygame.quit()
sys.exit()