import pygame
import random
import math

class NPC:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x - 15, y - 15, 30, 30)
        self.speed = 2
        self.direction = 0
        self.target_position = self.get_random_target()
        self.waiting = 0

    def get_random_target(self):
        # Get a random position on screen
        x = random.randint(50, 750)
        y = random.randint(50, 550)
        return pygame.Vector2(x, y)

    def update(self):
        if self.waiting > 0:
            self.waiting -= 1
            return

        # Move towards target
        to_target = self.target_position - self.position
        distance = to_target.length()

        if distance < 5:
            # Reached target, get new one and wait
            self.target_position = self.get_random_target()
            self.waiting = random.randint(60, 180)  # 1-3 seconds at 60 fps
        else:
            # Move towards target
            self.direction = math.atan2(to_target.y, to_target.x)
            if distance > 0:
                movement = to_target.normalize() * self.speed
                self.position += movement
                self.rect.center = self.position

    def draw(self, screen):
        # Draw NPC triangle
        points = [
            (self.position.x + math.cos(self.direction) * 15,
             self.position.y + math.sin(self.direction) * 15),
            (self.position.x + math.cos(self.direction + 2.6) * 15,
             self.position.y + math.sin(self.direction + 2.6) * 15),
            (self.position.x + math.cos(self.direction - 2.6) * 15,
             self.position.y + math.sin(self.direction - 2.6) * 15)
        ]
        pygame.draw.polygon(screen, (0, 0, 255), points)