import pygame
import math
import sys
import random

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.size = 32
        self.rect = pygame.Rect(x - self.size/2, y - self.size/2, self.size, self.size)

    def move(self, dx, dy, walls):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # Update rectangle position for collision detection
        new_rect = pygame.Rect(new_x - self.size/2, new_y - self.size/2, self.size, self.size)

        # Check collision with walls
        can_move = True
        for wall in walls:
            if new_rect.colliderect(wall):
                can_move = False
                break

        if can_move:
            self.x = new_x
            self.y = new_y
            self.rect = new_rect

class Map:
    def __init__(self):
        # Make the map much larger than the screen
        self.width = 2400  # 3x screen width
        self.height = 1800  # 3x screen height
        self.tile_size = 32
        self.walls = []
        self.roads = []
        self.create_city_layout()

    def create_city_layout(self):
        # Create a grid of roads
        road_width = 64
        block_size = 200

        # Create horizontal roads
        for y in range(0, self.height, block_size):
            self.roads.append(pygame.Rect(0, y, self.width, road_width))

        # Create vertical roads
        for x in range(0, self.width, block_size):
            self.roads.append(pygame.Rect(x, 0, road_width, self.height))

        # Create buildings in blocks
        for block_x in range(road_width, self.width - road_width, block_size):
            for block_y in range(road_width, self.height - road_width, block_size):
                # Add 2-3 buildings per block
                for _ in range(random.randint(2, 3)):
                    building_width = random.randint(50, 120)
                    building_height = random.randint(50, 120)
                    x = block_x + random.randint(0, block_size - building_width - road_width)
                    y = block_y + random.randint(0, block_size - building_height - road_width)
                    self.walls.append(pygame.Rect(x, y, building_width, building_height))

    def draw(self, screen, camera_x, camera_y):
        # Draw roads (dark gray)
        for road in self.roads:
            # Adjust position based on camera
            road_view = pygame.Rect(road.x - camera_x, road.y - camera_y, road.width, road.height)
            if road_view.colliderect(screen.get_rect()):
                pygame.draw.rect(screen, (50, 50, 50), road_view)

        # Draw buildings (gray)
        for wall in self.walls:
            # Adjust position based on camera
            wall_view = pygame.Rect(wall.x - camera_x, wall.y - camera_y, wall.width, wall.height)
            if wall_view.colliderect(screen.get_rect()):
                pygame.draw.rect(screen, (100, 100, 100), wall_view)

    def draw_minimap(self, screen, player_x, player_y):
        # Draw minimap in top-right corner
        minimap_size = 150
        margin = 10
        scale = minimap_size / max(self.width, self.height)

        # Draw minimap background
        minimap_rect = pygame.Rect(screen.get_width() - minimap_size - margin, 
                                 margin, minimap_size, minimap_size)
        pygame.draw.rect(screen, (0, 0, 0), minimap_rect)

        # Draw roads on minimap
        for road in self.roads:
            mini_road = pygame.Rect(
                screen.get_width() - minimap_size - margin + road.x * scale,
                margin + road.y * scale,
                road.width * scale,
                road.height * scale
            )
            pygame.draw.rect(screen, (100, 100, 100), mini_road)

        # Draw player on minimap
        player_pos = (
            screen.get_width() - minimap_size - margin + player_x * scale,
            margin + player_y * scale
        )
        pygame.draw.circle(screen, (255, 0, 0), 
                         (int(player_pos[0]), int(player_pos[1])), 3)

class Game:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("GTA Style Game")

        # Create game objects
        self.map = Map()
        # Start player in center of map
        self.player = Player(self.map.width/2, self.map.height/2)

        # Initialize camera to center on player
        self.camera_x = self.player.x - self.width/2
        self.camera_y = self.player.y - self.height/2

        # Game state
        self.running = True
        self.dragging = False
        self.last_mouse_pos = None

    def update_camera(self):
        # Camera follows player with some margin
        margin = 200

        # Update camera x position
        if self.player.x - self.camera_x < margin:
            self.camera_x = self.player.x - margin
        elif self.player.x - self.camera_x > self.width - margin:
            self.camera_x = self.player.x - (self.width - margin)

        # Update camera y position
        if self.player.y - self.camera_y < margin:
            self.camera_y = self.player.y - margin
        elif self.player.y - self.camera_y > self.height - margin:
            self.camera_y = self.player.y - (self.height - margin)

        # Keep camera within map bounds
        self.camera_x = max(0, min(self.camera_x, self.map.width - self.width))
        self.camera_y = max(0, min(self.camera_y, self.map.height - self.height))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.dragging = True
                self.last_mouse_pos = pygame.mouse.get_pos()

            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False

            elif event.type == pygame.MOUSEMOTION and self.dragging:
                current_pos = pygame.mouse.get_pos()
                if self.last_mouse_pos:
                    # Calculate direction based on screen position relative to player
                    screen_center_x = self.width / 2
                    screen_center_y = self.height / 2
                    dx = (current_pos[0] - screen_center_x) / screen_center_x
                    dy = (current_pos[1] - screen_center_y) / screen_center_y

                    # Normalize the vector
                    length = math.sqrt(dx * dx + dy * dy)
                    if length > 0:
                        dx /= length
                        dy /= length
                        self.player.move(dx, dy, self.map.walls)
                        self.update_camera()

    def draw(self):
        # Clear the screen
        self.screen.fill((34, 139, 34))  # Green background (grass)

        # Draw the map (adjusting for camera position)
        self.map.draw(self.screen, self.camera_x, self.camera_y)

        # Draw the player (adjusted for camera position)
        player_screen_x = self.player.x - self.camera_x
        player_screen_y = self.player.y - self.camera_y
        pygame.draw.rect(self.screen, (255, 0, 0),
                        (player_screen_x - self.player.size/2,
                         player_screen_y - self.player.size/2,
                         self.player.size,
                         self.player.size))

        # Draw minimap
        self.map.draw_minimap(self.screen, self.player.x, self.player.y)

        # Update the display
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            self.draw()
            clock.tick(60)  # 60 FPS

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()