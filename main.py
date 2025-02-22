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
        self.width = 3200  
        self.height = 2400  
        self.tile_size = 32
        self.walls = []
        self.roads = []
        self.vehicles = []
        self.window_states = {}
        self.districts = []  
        self.create_detroit_layout()
        self.spawn_vehicles(20)  

    def create_detroit_layout(self):
        # Main arterial roads based on Detroit's radial layout
        major_roads = [
            # Woodward Avenue (central diagonal)
            {"start": (self.width//2, 0), "end": (self.width//2, self.height), "width": 128},

            # Major radial avenues
            {"start": (0, self.height//2), "end": (self.width//2, self.height//4), "width": 96},
            {"start": (self.width//2, self.height//4), "end": (self.width, self.height//2), "width": 96},
            {"start": (0, 2*self.height//3), "end": (self.width, self.height//2), "width": 96},

            # Grand Boulevard (circular road)
            *[{"start": (self.width//2 + math.cos(angle)*800, self.height//2 + math.sin(angle)*800),
               "end": (self.width//2 + math.cos(angle + 0.5)*800, self.height//2 + math.sin(angle + 0.5)*800),
               "width": 96} for angle in range(0, 12)]
        ]

        # Create the roads with proper angles
        for road in major_roads:
            start = road["start"]
            end = road["end"]
            width = road["width"]

            # Calculate road angle and length
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            angle = math.atan2(dy, dx)
            length = math.sqrt(dx*dx + dy*dy)

            # Create a rectangle for the road at the correct angle
            road_surface = pygame.Surface((length, width), pygame.SRCALPHA)
            road_rect = pygame.Rect(start[0], start[1], length, width)
            road_rect.x = start[0]
            road_rect.y = start[1]


            self.roads.append({
                "rect": road_rect,
                "angle": math.degrees(angle),
                "major": True,
                "start": start,
                "end": end
            })

        # Create districts based on the provided map
        districts = [
            {"name": "Downtown", "center": (self.width//2, self.height//2), "radius": 400},
            {"name": "Midtown", "center": (self.width//2, self.height//3), "radius": 300},
            {"name": "New Center", "center": (self.width//2, self.height//4), "radius": 250},
            # Add more districts with proper positioning
        ]

        # Generate buildings based on district density
        for district in districts:
            density = 0.7 if district["name"] == "Downtown" else 0.4
            buildings_count = int(50 * density)

            for _ in range(buildings_count):
                angle = random.uniform(0, 2*math.pi)
                distance = random.uniform(0, district["radius"])
                x = district["center"][0] + math.cos(angle) * distance
                y = district["center"][1] + math.sin(angle) * distance

                # Don't place buildings on roads
                if not any(self.point_on_road((x, y), road) for road in self.roads):
                    building_size = random.randint(40, 100)
                    building_id = f"building_{x}_{y}"

                    self.walls.append({
                        "rect": pygame.Rect(x, y, building_size, building_size),
                        "color": (120, 120, 120),
                        "windows": {"rows": 3, "cols": 4},
                        "id": building_id
                    })

                    if building_id not in self.window_states:
                        self.window_states[building_id] = [
                            random.random() < 0.3 for _ in range(12)
                        ]

    def point_on_road(self, point, road):
        # Check if a point is on or near a road
        x, y = point
        for road in self.roads:
            if road["rect"].collidepoint(x, y):
                return True
        return False

    def spawn_player(self):
        # Spawn player on a major road
        valid_spawn = None
        while not valid_spawn:
            road = random.choice([r for r in self.roads if r.get("major")])
            x = (road["start"][0] + road["end"][0]) // 2
            y = (road["start"][1] + road["end"][1]) // 2

            # Check if spawn point is clear
            test_rect = pygame.Rect(x - 16, y - 16, 32, 32)
            if not any(wall["rect"].colliderect(test_rect) for wall in self.walls):
                valid_spawn = (x, y)

        return valid_spawn


    def draw(self, screen, camera_x, camera_y):
        for road in self.roads:
            road_view = pygame.Rect(
                road["rect"].x - camera_x,
                road["rect"].y - camera_y,
                road["rect"].width,
                road["rect"].height
            )
            if road_view.colliderect(screen.get_rect()):
                pygame.draw.rect(screen, (50, 50, 50), road_view)

                line_color = (255, 255, 255)
                if road["rect"].width > road["rect"].height:
                    line_y = road_view.centery
                    x = road["rect"].x - camera_x
                    while x < road["rect"].x + road["rect"].width - camera_x:
                        pygame.draw.line(screen, line_color,
                                       (x, line_y),
                                       (x + 20, line_y), 2)
                        x += 40
                else:
                    line_x = road_view.centerx
                    y = road["rect"].y - camera_y
                    while y < road["rect"].y + road["rect"].height - camera_y:
                        pygame.draw.line(screen, line_color,
                                       (line_x, y),
                                       (line_x, y + 20), 2)
                        y += 40

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
        os.environ['SDL_VIDEODRIVER'] = 'x11'

        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("GTA Style Game")

        self.map = Map()
        spawn_point = self.map.spawn_player()
        self.player = Player(spawn_point[0], spawn_point[1])

        self.camera_x = self.player.x - self.width/2
        self.camera_y = self.player.y - self.height/2

        self.running = True
        self.dragging = False
        self.last_mouse_pos = None

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
            dx = 0
            dy = 0

            if keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_d]: dx += 1
            if keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_s]: dy += 1

            if dx != 0 and dy != 0:
                dx *= 0.7071  
                dy *= 0.7071

            self.player.move(dx, dy, self.map.walls)
            self.update_camera()
        else:
            keys = pygame.key.get_pressed()
            forward = 0
            turn = 0

            if keys[pygame.K_w]: forward += 1
            if keys[pygame.K_s]: forward -= 1
            if keys[pygame.K_d]: turn += 1
            if keys[pygame.K_a]: turn -= 1

            self.player.in_vehicle.move(forward, turn, self.map.walls)
            self.player.x = self.player.in_vehicle.x
            self.player.y = self.player.in_vehicle.y
            self.update_camera()

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
    pygame.init()
    game = Game()
    game.run()