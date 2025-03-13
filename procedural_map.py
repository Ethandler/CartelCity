
import pygame
import random
import os
import numpy as np

def generate_city_map(width=2400, height=1800):
    """
    Generate a procedural city map with streets and buildings
    Returns a pygame Surface with the map
    """
    # Create a blank surface
    surface = pygame.Surface((width, height))
    
    # Fill with a light color as the base (ground)
    background_color = (150, 150, 120)
    surface.fill(background_color)
    
    # Create a grid of roads
    road_color = (50, 50, 50)
    block_size = 300  # City block size
    road_width = 80   # Width of roads
    
    # Generate main roads (grid)
    for x in range(0, width, block_size):
        pygame.draw.rect(surface, road_color, (x, 0, road_width, height))
    
    for y in range(0, height, block_size):
        pygame.draw.rect(surface, road_color, (0, y, width, road_width))
    
    # Add some diagonal roads
    for i in range(3):
        start_x = random.randint(0, width // 3)
        start_y = random.randint(0, height // 3)
        end_x = random.randint(width * 2 // 3, width)
        end_y = random.randint(height * 2 // 3, height)
        
        points = [(start_x, start_y)]
        
        # Generate points for the diagonal road
        num_points = 5
        for j in range(1, num_points):
            x = start_x + (end_x - start_x) * j // num_points
            y = start_y + (end_y - start_y) * j // num_points
            
            # Add some randomness
            x += random.randint(-50, 50)
            y += random.randint(-50, 50)
            
            points.append((x, y))
        
        points.append((end_x, end_y))
        
        # Draw the diagonal road
        pygame.draw.lines(surface, road_color, False, points, road_width)
    
    # Add buildings in the blocks
    for x in range(road_width, width, block_size):
        for y in range(road_width, height, block_size):
            # Skip if we're on a road
            if (x % block_size < road_width) or (y % block_size < road_width):
                continue
            
            # Determine block area
            block_width = min(block_size - road_width, width - x)
            block_height = min(block_size - road_width, height - y)
            
            # Add buildings in this block
            num_buildings = random.randint(3, 8)
            for _ in range(num_buildings):
                bldg_x = x + random.randint(20, block_width - 60)
                bldg_y = y + random.randint(20, block_height - 60)
                bldg_width = random.randint(40, 100)
                bldg_height = random.randint(40, 100)
                
                # Random building color
                bldg_color = random.choice([
                    (200, 200, 200),  # Light gray
                    (180, 180, 180),  # Medium gray
                    (160, 160, 160),  # Dark gray
                    (200, 180, 160),  # Tan
                    (170, 140, 120),  # Brown
                ])
                
                pygame.draw.rect(surface, bldg_color, (bldg_x, bldg_y, bldg_width, bldg_height))
    
    # Add some parks (green areas)
    for _ in range(10):
        park_x = random.randint(0, width - 200)
        park_y = random.randint(0, height - 200)
        park_width = random.randint(100, 300)
        park_height = random.randint(100, 300)
        
        # Park color
        park_color = (50, 150, 50)
        
        pygame.draw.rect(surface, park_color, (park_x, park_y, park_width, park_height))
    
    # Add some water features (blue areas)
    for _ in range(3):
        water_x = random.randint(0, width - 300)
        water_y = random.randint(0, height - 300)
        water_width = random.randint(200, 500)
        water_height = random.randint(200, 400)
        
        # Water color
        water_color = (50, 100, 200)
        
        pygame.draw.rect(surface, water_color, (water_x, water_y, water_width, water_height))
    
    return surface

def save_map(map_surface, filename="generated_map.jpeg"):
    """Save the generated map to a file"""
    # Ensure the directory exists
    os.makedirs("attached_assets", exist_ok=True)
    
    # Save the image
    pygame.image.save(map_surface, os.path.join("attached_assets", filename))
    
    return os.path.join("attached_assets", filename)

if __name__ == "__main__":
    pygame.init()
    city_map = generate_city_map()
    map_path = save_map(city_map)
    print(f"Map saved to {map_path}")
    pygame.quit()
