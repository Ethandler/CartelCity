import pygame
import math
import sys

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
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tile_size = 32
        self.walls = []
        self.create_boundary_walls()
        self.create_obstacles()

    def create_boundary_walls(self):
        # Create walls around the map
        wall_thickness = 32

        # Top wall
        self.walls.append(pygame.Rect(0, 0, self.width, wall_thickness))
        # Bottom wall
        self.walls.append(pygame.Rect(0, self.height - wall_thickness, self.width, wall_thickness))
        # Left wall
        self.walls.append(pygame.Rect(0, 0, wall_thickness, self.height))
        # Right wall
        self.walls.append(pygame.Rect(self.width - wall_thickness, 0, wall_thickness, self.height))

    def create_obstacles(self):
        # Add some building-like obstacles
        obstacles = [
            (200, 200, 100, 100),  # Building 1
            (500, 300, 150, 80),   # Building 2
            (300, 400, 80, 120),   # Building 3
        ]

        for obs in obstacles:
            self.walls.append(pygame.Rect(obs))

    def draw(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, (100, 100, 100), wall)  # Gray walls

class Game:
    def __init__(self):
        # Set up the display
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("GTA Style Game")

        # Create game objects
        self.map = Map(self.width, self.height)
        self.player = Player(self.width/2, self.height/2)

        # Game state
        self.running = True
        self.dragging = False
        self.last_mouse_pos = None

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
                    dx = current_pos[0] - self.last_mouse_pos[0]
                    dy = current_pos[1] - self.last_mouse_pos[1]
                    length = math.sqrt(dx * dx + dy * dy)
                    if length > 0:
                        dx /= length
                        dy /= length
                        self.player.move(dx, dy, self.map.walls)
                self.last_mouse_pos = current_pos

    def draw(self):
        # Clear the screen
        self.screen.fill((34, 139, 34))  # Green background (grass)

        # Draw the map
        self.map.draw(self.screen)

        # Draw the player
        pygame.draw.rect(self.screen, (255, 0, 0), self.player.rect)

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