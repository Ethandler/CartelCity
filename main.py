import pygame
import math
import sys
import random
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set SDL environment variables for better compatibility
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['SDL_RENDER_DRIVER'] = 'software'

class Vehicle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0
        self.max_speed = 6
        self.acceleration = 0.2
        self.rotation = 0
        self.size = (32, 16)
        self.rect = pygame.Rect(x - self.size[0]/2, y - self.size[1]/2, self.size[0], self.size[1])
        self.color = random.choice([
            (200, 0, 0),    # Red
            (0, 0, 200),    # Blue
            (40, 40, 40),   # Dark Gray
            (200, 200, 200),# Silver
            (255, 255, 255),# White
            (0, 100, 0),    # Dark Green
        ])

    def move(self, forward, turn, walls):
        if forward != 0:
            target_speed = forward * self.max_speed
            self.speed = min(max(self.speed + (self.acceleration * forward), -self.max_speed), self.max_speed)
        else:
            if abs(self.speed) > self.acceleration:
                self.speed -= (self.acceleration * (1 if self.speed > 0 else -1))
            else:
                self.speed = 0

        if turn:
            turn_rate = 3 * (1 - (abs(self.speed) / self.max_speed) * 0.5)
            self.rotation += turn * turn_rate
            self.rotation %= 360

        angle = math.radians(self.rotation)
        dx = math.cos(angle) * self.speed
        dy = math.sin(angle) * self.speed

        new_x = self.x + dx
        new_y = self.y + dy

        new_rect = pygame.Rect(new_x - self.size[0]/2, new_y - self.size[1]/2, self.size[0], self.size[1])

        can_move = True
        for wall in walls:
            if new_rect.colliderect(wall["rect"]):
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

        screen_rect = screen.get_rect()
        if (screen_x + self.size[0] < -50 or screen_x - self.size[0] > screen_rect.width + 50 or
            screen_y + self.size[1] < -50 or screen_y - self.size[1] > screen_rect.height + 50):
            return

        car_surface = pygame.Surface(self.size, pygame.SRCALPHA)

        pygame.draw.rect(car_surface, self.color, (0, 0, self.size[0], self.size[1]))

        window_color = (30, 30, 30, 200)
        window_width = self.size[0] // 4
        window_height = self.size[1] // 2

        pygame.draw.rect(car_surface, window_color, 
                        (self.size[0] - window_width - 4, 2, window_width, window_height))
        pygame.draw.rect(car_surface, window_color,
                        (4, 2, window_width, window_height))

        light_size = 3
        if self.rotation in [0, 180]:
            pygame.draw.rect(car_surface, (255, 255, 200),
                           (self.size[0] - light_size - 1, 2, light_size, light_size))
            pygame.draw.rect(car_surface, (255, 255, 200),
                           (self.size[0] - light_size - 1, self.size[1] - light_size - 2, light_size, light_size))
            pygame.draw.rect(car_surface, (255, 0, 0),
                           (1, 2, light_size, light_size))
            pygame.draw.rect(car_surface, (255, 0, 0),
                           (1, self.size[1] - light_size - 2, light_size, light_size))

        rotated_surface = pygame.transform.rotate(car_surface, -self.rotation)

        screen.blit(rotated_surface, (screen_x - rotated_surface.get_width()/2,
                                    screen_y - rotated_surface.get_height()/2))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3
        self.size = 16
        self.rect = pygame.Rect(x - self.size/2, y - self.size/2, self.size, self.size)
        self.direction = 'down'
        self.moving = False
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.colors = {
            'skin': (255, 223, 196),
            'shirt': (200, 0, 0),
            'pants': (0, 0, 150),
            'shoes': (40, 40, 40),
            'eyes': (0, 0, 0)
        }
        self.in_vehicle = None
        self.vehicle_entry_cooldown = 0

    def move(self, dx, dy, walls):
        if dx != 0 or dy != 0:
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
            self.moving = True
        else:
            self.moving = False

        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        if self.moving:
            self.animation_frame = (self.animation_frame + self.animation_speed) % 4
        else:
            self.animation_frame = 0

        new_rect = pygame.Rect(new_x - self.size/2, new_y - self.size/2, self.size, self.size)

        can_move = True
        for wall in walls:
            if new_rect.colliderect(wall["rect"]):
                can_move = False
                break

        if can_move:
            self.x = new_x
            self.y = new_y
            self.rect = new_rect

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        char_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

        walk_offset = math.sin(self.animation_frame * math.pi) * 2 if self.moving else 0
        head_bob = math.sin(self.animation_frame * math.pi * 2) * 1.5

        head_top = self.size - head_bob
        head_bottom = self.size + head_bob
        head_width = self.size * 0.8

        pygame.draw.ellipse(
            char_surface,
            self.colors['skin'],
            (self.size - head_width/2, head_top - head_width/2, head_width, head_width)
        )

        pygame.draw.ellipse(
            char_surface,
            self.colors['skin'],
            (self.size - head_width/2, head_bottom - head_width/2, head_width * 0.8, head_width * 0.4)
        )

        eye_size = 2
        eye_spacing = 4
        pygame.draw.circle(
            char_surface,
            self.colors['eyes'],
            (self.size - eye_spacing, self.size),
            eye_size
        )
        pygame.draw.circle(
            char_surface,
            self.colors['eyes'],
            (self.size + eye_spacing, self.size),
            eye_size
        )

        body_points = [
            (self.size - self.size * 0.3, self.size + head_width * 0.3),
            (self.size + self.size * 0.3, self.size + head_width * 0.3),
            (self.size + self.size * 0.4, self.size + self.size * 0.6),
            (self.size - self.size * 0.4, self.size + self.size * 0.6)
        ]
        pygame.draw.polygon(char_surface, self.colors['shirt'], body_points)

        if self.moving:
            leg_offset = walk_offset * 1.5
            left_leg = [
                (self.size - self.size * 0.25, self.size + self.size * 0.5),
                (self.size - self.size * 0.15, self.size + self.size * 0.5),
                (self.size - self.size * 0.2 + leg_offset, self.size + self.size * 0.8),
                (self.size - self.size * 0.3 + leg_offset, self.size + self.size * 0.8)
            ]
            right_leg = [
                (self.size + self.size * 0.15, self.size + self.size * 0.5),
                (self.size + self.size * 0.25, self.size + self.size * 0.5),
                (self.size + self.size * 0.3 - leg_offset, self.size + self.size * 0.8),
                (self.size + self.size * 0.2 - leg_offset, self.size + self.size * 0.8)
            ]
            pygame.draw.polygon(char_surface, self.colors['pants'], left_leg)
            pygame.draw.polygon(char_surface, self.colors['pants'], right_leg)

            pygame.draw.circle(char_surface, self.colors['shoes'],
                             (self.size - self.size * 0.25 + leg_offset, self.size + self.size * 0.8), 3)
            pygame.draw.circle(char_surface, self.colors['shoes'],
                             (self.size + self.size * 0.25 - leg_offset, self.size + self.size * 0.8), 3)
        else:
            left_leg = [
                (self.size - self.size * 0.25, self.size + self.size * 0.5),
                (self.size - self.size * 0.15, self.size + self.size * 0.5),
                (self.size - self.size * 0.2, self.size + self.size * 0.8),
                (self.size - self.size * 0.3, self.size + self.size * 0.8)
            ]
            right_leg = [
                (self.size + self.size * 0.15, self.size + self.size * 0.5),
                (self.size + self.size * 0.25, self.size + self.size * 0.5),
                (self.size + self.size * 0.3, self.size + self.size * 0.8),
                (self.size + self.size * 0.2, self.size + self.size * 0.8)
            ]
            pygame.draw.polygon(char_surface, self.colors['pants'], left_leg)
            pygame.draw.polygon(char_surface, self.colors['pants'], right_leg)

            pygame.draw.circle(char_surface, self.colors['shoes'],
                             (self.size - self.size * 0.25, self.size + self.size * 0.8), 3)
            pygame.draw.circle(char_surface, self.colors['shoes'],
                             (self.size + self.size * 0.25, self.size + self.size * 0.8), 3)

        if self.direction == 'left':
            char_surface = pygame.transform.flip(char_surface, True, False)

        screen.blit(char_surface, 
                   (screen_x - char_surface.get_width()/2,
                    screen_y - char_surface.get_height()/2))

    def enter_exit_vehicle(self, vehicles):
        if self.vehicle_entry_cooldown > 0:
            return

        if self.in_vehicle:
            self.x = self.in_vehicle.x + math.cos(math.radians(self.in_vehicle.rotation)) * 40
            self.y = self.in_vehicle.y + math.sin(math.radians(self.in_vehicle.rotation)) * 40
            self.rect = pygame.Rect(self.x - self.size/2, self.y - self.size/2, self.size, self.size)
            self.in_vehicle = None
            self.vehicle_entry_cooldown = 30
        else:
            for vehicle in vehicles:
                dist = math.sqrt((self.x - vehicle.x)**2 + (self.y - vehicle.y)**2)
                if dist < 50:
                    self.in_vehicle = vehicle
                    self.vehicle_entry_cooldown = 30
                    break

    def update(self):
        if self.vehicle_entry_cooldown > 0:
            self.vehicle_entry_cooldown -= 1

class Map:
    def __init__(self):
        self.width = 2400
        self.height = 1800
        self.tile_size = 32
        self.walls = []
        self.roads = []
        self.sidewalks = []
        self.vehicles = []
        self.window_states = {}
        self.create_city_layout()
        self.spawn_vehicles(15)

    def create_city_layout(self):
        highway_width = 160
        main_road_width = 96
        side_road_width = 64
        sidewalk_width = 16
        block_size = 300
        min_building_margin = 20

        # Create highways
        highway_positions = [self.height // 3, (2 * self.height) // 3]
        for y in highway_positions:
            road = pygame.Rect(0, y - highway_width//2, self.width, highway_width)
            self.roads.append({"rect": road, "horizontal": True, "type": "highway"})

            self.sidewalks.append(pygame.Rect(0, y - highway_width//2 - sidewalk_width, self.width, sidewalk_width))
            self.sidewalks.append(pygame.Rect(0, y + highway_width//2, self.width, sidewalk_width))

        highway_positions = [self.width // 3, (2 * self.width) // 3]
        for x in highway_positions:
            road = pygame.Rect(x - highway_width//2, 0, highway_width, self.height)
            self.roads.append({"rect": road, "horizontal": False, "type": "highway"})

            self.sidewalks.append(pygame.Rect(x - highway_width//2 - sidewalk_width, 0, sidewalk_width, self.height))
            self.sidewalks.append(pygame.Rect(x + highway_width//2, 0, sidewalk_width, self.height))

        # Create regular roads
        for i in range(0, self.height, block_size):
            if i not in [pos - highway_width//2 for pos in highway_positions]:
                width = main_road_width if i % (block_size * 2) == 0 else side_road_width
                road = pygame.Rect(0, i, self.width, width)
                self.roads.append({"rect": road, "horizontal": True, "type": "main" if width == main_road_width else "side"})

                self.sidewalks.append(pygame.Rect(0, i - sidewalk_width, self.width, sidewalk_width))
                self.sidewalks.append(pygame.Rect(0, i + width, self.width, sidewalk_width))

        for i in range(0, self.width, block_size):
            if i not in [pos - highway_width//2 for pos in highway_positions]:
                width = main_road_width if i % (block_size * 2) == 0 else side_road_width
                road = pygame.Rect(i, 0, width, self.height)
                self.roads.append({"rect": road, "horizontal": False, "type": "main" if width == main_road_width else "side"})

                self.sidewalks.append(pygame.Rect(i - sidewalk_width, 0, sidewalk_width, self.height))
                self.sidewalks.append(pygame.Rect(i + width, 0, sidewalk_width, self.height))

        # Building generation
        building_colors = [
            (120, 120, 120),  # Gray
            (180, 100, 100),  # Brick Red
            (100, 130, 150),  # Blue Gray
            (150, 150, 130),  # Beige
        ]

        for block_x in range(highway_width, self.width - highway_width, block_size):
            for block_y in range(highway_width, self.height - highway_width, block_size):
                available_width = block_size - highway_width - min_building_margin * 2
                available_height = block_size - highway_width - min_building_margin * 2

                if available_width <= 0 or available_height <= 0:
                    continue

                for _ in range(random.randint(1, 2)):  # Reduced from 2-3 to 1-2 buildings per block
                    max_building_width = min(160, available_width)
                    max_building_height = min(160, available_height)
                    min_building_size = 60  # Reduced from 80

                    if max_building_width <= min_building_size or max_building_height <= min_building_size:
                        continue

                    building_width = random.randint(min_building_size, max_building_width)
                    building_height = random.randint(min_building_size, max_building_height)

                    # Calculate safe random position range
                    max_x_offset = block_size - building_width - highway_width - min_building_margin
                    max_y_offset = block_size - building_height - highway_width - min_building_margin

                    if max_x_offset <= 0 or max_y_offset <= 0:
                        continue

                    x = block_x + random.randint(min_building_margin, max_x_offset)
                    y = block_y + random.randint(min_building_margin, max_y_offset)

                    building_id = f"building_{x}_{y}"
                    self.walls.append({
                        "rect": pygame.Rect(x, y, building_width, building_height),
                        "color": random.choice(building_colors),
                        "windows": {
                            "rows": random.randint(2, 4),
                            "cols": random.randint(3, 5)
                        },
                        "id": building_id
                    })

                    if building_id not in self.window_states:
                        self.window_states[building_id] = []
                        for _ in range(16):
                            self.window_states[building_id].append(random.random() < 0.3)

    def draw(self, screen, camera_x, camera_y):
        for road in self.roads:
            road_view = pygame.Rect(
                road["rect"].x - camera_x,
                road["rect"].y - camera_y,
                road["rect"].width,
                road["rect"].height
            )
            if road_view.colliderect(screen.get_rect()):
                road_color = (40, 40, 40) if road["type"] == "highway" else (50, 50, 50)
                pygame.draw.rect(screen, road_color, road_view)

                line_color = (255, 255, 0) if road["type"] == "highway" else (255, 255, 255)
                line_width = 3 if road["type"] == "highway" else 2

                if road["horizontal"]:
                    if road["type"] == "highway":
                        line_y1 = road_view.centery - 2
                        line_y2 = road_view.centery + 2
                        x = road["rect"].x - camera_x
                        while x < road["rect"].x + road["rect"].width - camera_x:
                            pygame.draw.line(screen, line_color, (x, line_y1), (x + 30, line_y1), line_width)
                            pygame.draw.line(screen, line_color, (x, line_y2), (x + 30, line_y2), line_width)
                            x += 40
                    else:
                        line_y = road_view.centery
                        x = road["rect"].x - camera_x
                        while x < road["rect"].x + road["rect"].width - camera_x:
                            pygame.draw.line(screen, line_color, (x, line_y), (x + 20, line_y), line_width)
                            x += 40
                else:
                    if road["type"] == "highway":
                        line_x1 = road_view.centerx - 2
                        line_x2 = road_view.centerx + 2
                        y = road["rect"].y - camera_y
                        while y < road["rect"].y + road["rect"].height - camera_y:
                            pygame.draw.line(screen, line_color, (line_x1, y), (line_x1, y + 30), line_width)
                            pygame.draw.line(screen, line_color, (line_x2, y), (line_x2, y + 30), line_width)
                            y += 40
                    else:
                        line_x = road_view.centerx
                        y = road["rect"].y - camera_y
                        while y < road["rect"].y + road["rect"].height - camera_y:
                            pygame.draw.line(screen, line_color, (line_x, y), (line_x, y + 20), line_width)
                            y += 40

        for sidewalk in self.sidewalks:
            sidewalk_view = pygame.Rect(
                sidewalk.x - camera_x,
                sidewalk.y - camera_y,
                sidewalk.width,
                sidewalk.height
            )
            if sidewalk_view.colliderect(screen.get_rect()):
                pygame.draw.rect(screen, (150, 150, 150), sidewalk_view)

        for wall in self.walls:
            wall_view = pygame.Rect(
                wall["rect"].x - camera_x,
                wall["rect"].y - camera_y,
                wall["rect"].width,
                wall["rect"].height
            )
            if wall_view.colliderect(screen.get_rect()):
                pygame.draw.rect(screen, wall["color"], wall_view)

                window_width = wall["rect"].width // (wall["windows"]["cols"] * 2)
                window_height = wall["rect"].height // (wall["windows"]["rows"] * 2)
                window_index = 0
                for row in range(wall["windows"]["rows"]):
                    for col in range(wall["windows"]["cols"]):
                        if window_index < len(self.window_states[wall["id"]]):
                            window_x = wall_view.x + (col * 2 + 1) * window_width
                            window_y = wall_view.y + (row * 2 + 1) * window_height
                            window_color = (255, 255, 200) if self.window_states[wall["id"]][window_index] else (30, 30, 30)
                            pygame.draw.rect(screen, window_color,
                                             (window_x, window_y, window_width * 0.8, window_height * 0.8))
                            window_index += 1

        for vehicle in self.vehicles:
            vehicle.draw(screen, camera_x, camera_y)

    def draw_minimap(self, screen, player_x, player_y):
        minimap_size = 150
        margin = 10
        scale = minimap_size / max(self.width, self.height)

        minimap_rect = pygame.Rect(screen.get_width() - minimap_size - margin, 
                                 margin, minimap_size, minimap_size)
        pygame.draw.rect(screen, (0, 0, 0), minimap_rect)

        for road in self.roads:
            mini_road = pygame.Rect(
                screen.get_width() - minimap_size - margin + road["rect"].x * scale,
                margin + road["rect"].y * scale,
                road["rect"].width * scale,
                road["rect"].height * scale
            )
            pygame.draw.rect(screen, (100, 100, 100), mini_road)

        player_pos = (
            screen.get_width() - minimap_size - margin + player_x * scale,
            margin + player_y * scale
        )
        pygame.draw.circle(screen, (255, 0, 0), 
                         (int(player_pos[0]), int(player_pos[1])), 3)

    def spawn_vehicles(self, count):
        for _ in range(count):
            if not self.roads:
                return

            road = random.choice(self.roads)

            is_horizontal = road["rect"].width > road["rect"].height

            if is_horizontal:
                x = road["rect"].x + random.randint(0, road["rect"].width - 32)
                y = road["rect"].y + road["rect"].height // 2
                rotation = 0 if random.random() > 0.5 else 180
            else:
                x = road["rect"].x + road["rect"].width // 2
                y = road["rect"].y + random.randint(0, road["rect"].height - 32)
                rotation = 90 if random.random() > 0.5 else 270

            vehicle = Vehicle(x, y)
            vehicle.rotation = rotation
            self.vehicles.append(vehicle)

class Game:
    def __init__(self):
        try:
            logger.info("Initializing Pygame...")
            pygame.init()

            logger.info("Setting up display...")
            self.width = 800
            self.height = 600

            # Try to create the display with software rendering
            try:
                self.screen = pygame.display.set_mode(
                    (self.width, self.height),
                    pygame.SWSURFACE | pygame.HWSURFACE
                )
            except pygame.error as e:
                logger.error(f"Failed to create display: {e}")
                # Fallback to minimal display mode
                self.screen = pygame.display.set_mode(
                    (self.width, self.height),
                    pygame.SWSURFACE
                )

            pygame.display.set_caption("GTA Style Game")
            logger.info("Display setup complete")

            self.map = Map()
            self.player = Player(self.map.width/2, self.map.height/2)
            self.camera_x = self.player.x - self.width/2
            self.camera_y = self.player.y - self.height/2
            self.running = True
            self.dragging = False
            self.last_mouse_pos = None

        except Exception as e:
            logger.error(f"Failed to initialize game: {e}")
            pygame.quit()
            sys.exit(1)

    def update_camera(self):
        margin = 200

        if self.player.x - self.camera_x < margin:
            self.camera_x = self.player.x - margin
        elif self.player.x - self.camera_x > self.width - margin:
            self.camera_x = self.player.x - (self.width - margin)

        if self.player.y - self.camera_y < margin:
            self.camera_y = self.player.y - margin
        elif self.player.y - self.camera_y > self.height - margin:
            self.camera_y = self.player.y - (self.height - margin)

        self.camera_x = max(0, min(self.camera_x, self.map.width - self.width))
        self.camera_y = max(0, min(self.camera_y, self.map.height - self.height))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.player.enter_exit_vehicle(self.map.vehicles)

        if not self.player.in_vehicle:
            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_d] - keys[pygame.K_a]
            dy = keys[pygame.K_s] - keys[pygame.K_w]

            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071

            self.player.move(dx, dy, self.map.walls)
            self.update_camera()
        else:
            keys = pygame.key.get_pressed()
            forward = keys[pygame.K_w] - keys[pygame.K_s]
            turn = keys[pygame.K_d] - keys[pygame.K_a]
            self.player.in_vehicle.move(forward, turn, self.map.walls)
            self.player.x = self.player.in_vehicle.x
            self.player.y = self.player.in_vehicle.y

    def draw(self):
        self.screen.fill((34, 139, 34))

        self.map.draw(self.screen, self.camera_x, self.camera_y)

        if not self.player.in_vehicle:
            self.player.draw(self.screen, self.camera_x, self.camera_y)

        self.map.draw_minimap(self.screen, self.player.x, self.player.y)

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.player.update()
            self.handle_events()
            self.draw()
            clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()