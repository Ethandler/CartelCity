import pygame
import math

class Player:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x - 15, y - 15, 30, 30)
        self.speed = 5
        self.velocity = pygame.Vector2(0, 0)
        self.direction = 0  # angle in radians

        # Animation states
        self.walking = False
        self.frame_count = 0
        self.current_frame = 0

    def update(self):
        # Update position based on velocity
        self.position += self.velocity
        self.rect.center = self.position

        # Update animation
        if self.walking:
            self.frame_count += 1
            if self.frame_count % 10 == 0:
                self.current_frame = (self.current_frame + 1) % 4

    def move(self, dx, dy):
        # Update velocity based on input
        self.velocity.x = dx
        self.velocity.y = dy

        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize() * self.speed
            self.direction = math.atan2(dy, dx)
            self.walking = True

    def stop(self):
        self.velocity = pygame.Vector2(0, 0)
        self.walking = False

    def handle_collision(self):
        # Basic collision response
        self.velocity = pygame.Vector2(0, 0)

    def perform_action(self):
        # Placeholder for action (e.g., shooting, interaction)
        pass

    def draw(self, screen):
        # Draw player triangle
        points = [
            (self.position.x + math.cos(self.direction) * 15,
             self.position.y + math.sin(self.direction) * 15),
            (self.position.x + math.cos(self.direction + 2.6) * 15,
             self.position.y + math.sin(self.direction + 2.6) * 15),
            (self.position.x + math.cos(self.direction - 2.6) * 15,
             self.position.y + math.sin(self.direction - 2.6) * 15)
        ]
        pygame.draw.polygon(screen, (255, 0, 0), points)