import pygame
from player import Player
from npc import NPC
from map import GameMap

class GameScene:
    def __init__(self, screen):
        self.screen = screen
        self.background_color = (51, 51, 51)

        # Initialize game map
        self.game_map = GameMap(screen)

        # Initialize player
        screen_rect = screen.get_rect()
        self.player = Player(screen_rect.centerx, screen_rect.centery)

        # Initialize NPCs
        self.npcs = [
            NPC(100, 100),
            NPC(200, 200),
            NPC(300, 300)
        ]

        # Touch/mouse controls
        self.moving = False
        self.movement_target = None

    def update(self):
        # Update player position and state
        self.player.update()

        # Update NPCs
        for npc in self.npcs:
            npc.update()

        # Check collisions
        self.check_collisions()

    def check_collisions(self):
        # Check player collision with map objects
        for wall in self.game_map.walls:
            if self.player.rect.colliderect(wall):
                self.player.handle_collision()

        # Check player collision with NPCs
        for npc in self.npcs:
            if self.player.rect.colliderect(npc.rect):
                self.player.handle_collision()

    def draw(self):
        # Draw map
        self.game_map.draw(self.screen)

        # Draw NPCs
        for npc in self.npcs:
            npc.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Set movement target
            self.movement_target = event.pos
            self.moving = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.moving = False
        elif event.type == pygame.KEYDOWN:
            # Handle keyboard controls
            if event.key == pygame.K_SPACE:
                self.player.perform_action()
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d):
                self.player.stop()

        # Handle continuous keyboard input
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] - keys[pygame.K_a]) * self.player.speed
        dy = (keys[pygame.K_s] - keys[pygame.K_w]) * self.player.speed
        if dx != 0 or dy != 0:
            self.player.move(dx, dy)