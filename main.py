import pygame
import math
import sys
import random
import os

class Vehicle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0
        self.max_speed = 8
        self.acceleration = 0.2
        self.rotation = 0
        self.size = (48, 24)  # width, height
        self.rect = pygame.Rect(x - self.size[0]/2, y - self.size[1]/2, self.size[0], self.size[1])
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    def move(self, forward, turn, walls):
        # Update speed based on acceleration
        if forward:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif self.speed > 0:
            self.speed = max(0, self.speed - self.acceleration)

        # Update rotation
        if turn:
            self.rotation += turn * (3 if self.speed > 0 else 0)
            self.rotation %= 360

        # Calculate movement vector
        angle = math.radians(self.rotation)
        dx = math.cos(angle) * self.speed
        dy = math.sin(angle) * self.speed

        # Update position
        new_x = self.x + dx
        new_y = self.y + dy

        # Update rectangle for collision detection
        new_rect = pygame.Rect(new_x - self.size[0]/2, new_y - self.size[1]/2, self.size[0], self.size[1])

        # Check collision
        can_move = True
        for wall in walls:
            if new_rect.colliderect(wall):
                can_move = False
                self.speed = 0
                break

        if can_move:
            self.x = new_x
            self.y = new_y
            self.rect = new_rect

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # Create a surface for the rotated car
        car_surface = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(car_surface, self.color, (0, 0, self.size[0], self.size[1]))

        # Rotate the surface
        rotated_surface = pygame.transform.rotate(car_surface, -self.rotation)
        screen.blit(rotated_surface, (screen_x - rotated_surface.get_width()/2, 
                                    screen_y - rotated_surface.get_height()/2))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.size = 32
        self.rect = pygame.Rect(x - self.size/2, y - self.size/2, self.size, self.size)
        self.direction = 'down'  # Current facing direction
        self.moving = False
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.colors = {
            'body': (255, 0, 0),
            'head': (255, 200, 150),
            'legs': (0, 0, 255)
        }
        self.in_vehicle = None
        self.vehicle_entry_cooldown = 0
        self.size = 32  # Keep existing attributes...

    def move(self, dx, dy, walls):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # Update direction based on movement
        if abs(dx) > abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'down' if dy > 0 else 'up'

        # Update moving state and animation
        self.moving = dx != 0 or dy != 0
        if self.moving:
            self.animation_frame = (self.animation_frame + self.animation_speed) % 4
        else:
            self.animation_frame = 0

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

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # Draw basic animated character
        # Body
        body_rect = pygame.Rect(
            screen_x - self.size/2,
            screen_y - self.size/2,
            self.size,
            self.size
        )
        pygame.draw.rect(screen, self.colors['body'], body_rect)

        # Head
        head_size = self.size // 2
        head_y_offset = math.sin(self.animation_frame * math.pi) * 2 if self.moving else 0
        pygame.draw.circle(
            screen,
            self.colors['head'],
            (int(screen_x), int(screen_y - self.size/2 + head_y_offset)),
            head_size // 2
        )

        # Legs animation
        if self.moving:
            leg_offset = math.sin(self.animation_frame * math.pi) * 5
            # Left leg
            pygame.draw.rect(screen, self.colors['legs'],
                           (screen_x - self.size/4 - 2,
                            screen_y + self.size/4,
                            4,
                            self.size/2 + leg_offset))
            # Right leg
            pygame.draw.rect(screen, self.colors['legs'],
                           (screen_x + self.size/4 - 2,
                            screen_y + self.size/4,
                            4,
                            self.size/2 - leg_offset))

    def enter_exit_vehicle(self, vehicles):
        if self.vehicle_entry_cooldown > 0:
            return

        if self.in_vehicle:
            # Exit vehicle
            self.x = self.in_vehicle.x + math.cos(math.radians(self.in_vehicle.rotation)) * 40
            self.y = self.in_vehicle.y + math.sin(math.radians(self.in_vehicle.rotation)) * 40
            self.in_vehicle = None
            self.vehicle_entry_cooldown = 30
        else:
            # Try to enter nearest vehicle
            for vehicle in vehicles:
                dist = math.sqrt((self.x - vehicle.x)**2 + (self.y - vehicle.y)**2)
                if dist < 50:  # Entry range
                    self.in_vehicle = vehicle
                    self.vehicle_entry_cooldown = 30
                    break

    def update(self):
        if self.vehicle_entry_cooldown > 0:
            self.vehicle_entry_cooldown -= 1

class Map:
    def __init__(self):
        # Make the map much larger than the screen
        self.width = 2400  # 3x screen width
        self.height = 1800  # 3x screen height
        self.tile_size = 32
        self.walls = []
        self.roads = []
        self.vehicles = []
        self.create_city_layout()
        self.spawn_vehicles(5)  # Spawn initial vehicles

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

    def spawn_vehicles(self, count):
        for _ in range(count):
            # Find a random road
            road = random.choice(self.roads)
            # Spawn vehicle at random position on road
            x = road.x + random.randint(0, road.width)
            y = road.y + random.randint(0, road.height)
            self.vehicles.append(Vehicle(x, y))


class Game:
    def __init__(self):
        # Set SDL variables for Replit environment
        os.environ['SDL_VIDEODRIVER'] = 'x11'

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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.player.enter_exit_vehicle(self.map.vehicles)

            # Handle existing mouse events only when not in vehicle
            elif not self.player.in_vehicle:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.dragging = True
                    self.last_mouse_pos = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False

        # Handle vehicle controls
        if self.player.in_vehicle:
            keys = pygame.key.get_pressed()
            forward = keys[pygame.K_w] - keys[pygame.K_s]
            turn = keys[pygame.K_d] - keys[pygame.K_a]
            self.player.in_vehicle.move(forward, turn, self.map.walls)
            # Update player position to match vehicle
            self.player.x = self.player.in_vehicle.x
            self.player.y = self.player.in_vehicle.y
        elif self.dragging:  # Only handle mouse movement when not in vehicle
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

        # Draw vehicles
        for vehicle in self.map.vehicles:
            vehicle.draw(self.screen, self.camera_x, self.camera_y)

        # Draw the player with animations
        if not self.player.in_vehicle:
            self.player.draw(self.screen, self.camera_x, self.camera_y)

        # Draw minimap
        self.map.draw_minimap(self.screen, self.player.x, self.player.y)

        # Update the display
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.player.update()
            self.handle_events()
            self.draw()
            clock.tick(60)  # 60 FPS

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()