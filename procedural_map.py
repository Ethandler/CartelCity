
import pygame
import random
import os
import numpy as np

def generate_city_map(width=2400, height=1800):
    """
    Generate a procedural city map with streets and buildings styled like GTA 1
    Returns a pygame Surface with the map and a list of building rectangles for collision
    """
    # Create a blank surface
    surface = pygame.Surface((width, height))
    
    # Create a numpy array for collision map (1 = collision, 0 = passable)
    collision_map = np.zeros((width, height), dtype=np.int8)
    building_rects = []  # List to store building rectangles
    
    # Fill with a dark gray color as the street base (asphalt)
    street_color = (60, 60, 60)  # Dark gray for streets
    surface.fill(street_color)
    
    # Use a more organized grid like in GTA 1
    block_size = 320  # GTA-style city block size
    road_width = 120  # Main road width
    
    # Sidewalk colors and parameters
    sidewalk_color = (180, 180, 180)  # Light gray for sidewalks
    sidewalk_width = 30  # Width of sidewalks
    
    # Street parameters
    street_line_color = (220, 220, 0)  # Yellow street lines
    lane_width = 20  # Width of each lane
    
    # Grid of blocks and streets
    blocks = []  # Store blocks for building placement
    
    # 1. Create grid of blocks with proper streets between them
    for x in range(0, width, block_size):
        for y in range(0, height, block_size):
            # Calculate block area (considering streets)
            block_x = x + road_width // 2
            block_y = y + road_width // 2
            block_w = block_size - road_width
            block_h = block_size - road_width
            
            # Ensure we don't go beyond the map boundaries
            if block_x + block_w > width:
                block_w = width - block_x
            if block_y + block_h > height:
                block_h = height - block_y
                
            # Only add if we have a valid block
            if block_w > 0 and block_h > 0:
                blocks.append((block_x, block_y, block_w, block_h))
                
                # Draw sidewalks around the block (like in GTA 1)
                pygame.draw.rect(surface, sidewalk_color, 
                                (block_x - sidewalk_width, block_y - sidewalk_width, 
                                 block_w + sidewalk_width*2, block_h + sidewalk_width*2))
                
                # Draw the block interior (grass/dirt)
                block_interior_color = (100, 120, 80)  # Slightly green for grass/lots
                pygame.draw.rect(surface, block_interior_color, (block_x, block_y, block_w, block_h))
    
    # 2. Add yellow street lines on horizontal streets
    for y in range(road_width // 2, height, block_size):
        # Skip if too close to edge
        if y >= height - road_width // 2:
            continue
            
        # Center line
        line_y = y
        for x in range(0, width, 40):  # Dashed lines
            if x + 20 < width:
                pygame.draw.rect(surface, street_line_color, (x, line_y - 2, 20, 4))
    
    # 3. Add yellow street lines on vertical streets
    for x in range(road_width // 2, width, block_size):
        # Skip if too close to edge
        if x >= width - road_width // 2:
            continue
            
        # Center line
        line_x = x
        for y in range(0, height, 40):  # Dashed lines
            if y + 20 < height:
                pygame.draw.rect(surface, street_line_color, (line_x - 2, y, 4, 20))
    
    # 4. Add buildings in blocks
    for block_x, block_y, block_w, block_h in blocks:
        # Determine if this should be a special block (park, parking lot, etc.)
        block_type = random.choices(
            ["buildings", "park", "parking", "special"],
            weights=[0.7, 0.1, 0.15, 0.05],
            k=1
        )[0]
        
        if block_type == "buildings":
            # Standard building block
            
            # Number of buildings depends on block size
            building_density = max(1, int((block_w * block_h) / 15000))
            num_buildings = random.randint(building_density, building_density + 2)
            
            # Create organized building arrangement
            building_margin = 20  # Space between buildings
            min_bldg_size = 60    # Minimum building size
            
            # Try a grid-like arrangement of buildings
            grid_cols = min(3, max(1, int(block_w / 120)))
            grid_rows = min(3, max(1, int(block_h / 120)))
            
            if grid_cols * grid_rows > 0:
                cell_width = (block_w - building_margin) / grid_cols
                cell_height = (block_h - building_margin) / grid_rows
                
                for row in range(grid_rows):
                    for col in range(grid_cols):
                        # 30% chance to skip a building to create variation
                        if random.random() < 0.3:
                            continue
                            
                        # Calculate building position
                        bldg_x = block_x + col * cell_width + building_margin/2
                        bldg_y = block_y + row * cell_height + building_margin/2
                        
                        # Randomize building size slightly but maintain grid alignment
                        bldg_width = cell_width - building_margin - random.randint(0, 20)
                        bldg_height = cell_height - building_margin - random.randint(0, 20)
                        
                        # Ensure minimum size
                        if bldg_width < min_bldg_size or bldg_height < min_bldg_size:
                            continue
                            
                        # Choose a building color based on GTA 1 palette
                        bldg_color = random.choice([
                            (180, 180, 190),  # Light gray
                            (160, 160, 170),  # Medium gray
                            (140, 140, 150),  # Dark gray
                            (180, 160, 130),  # Tan
                            (150, 120, 100),  # Brown
                            (170, 150, 160),  # Mauve
                            (200, 180, 160),  # Beige
                        ])
                        
                        # Draw building
                        rect = pygame.Rect(int(bldg_x), int(bldg_y), int(bldg_width), int(bldg_height))
                        pygame.draw.rect(surface, bldg_color, rect)
                        
                        # Add to collision rectangles
                        building_rects.append(rect)
                        
                        # Add details to buildings (windows, doors)
                        add_building_details(surface, rect, bldg_color)
        
        elif block_type == "park":
            # Create a park with trees and paths
            park_color = (40, 120, 40)  # Darker green for parks
            pygame.draw.rect(surface, park_color, (block_x, block_y, block_w, block_h))
            
            # Add paths
            path_color = (170, 170, 150)
            path_width = 12
            
            # Horizontal path
            pygame.draw.rect(surface, path_color, 
                           (block_x, block_y + block_h//2 - path_width//2, 
                            block_w, path_width))
                            
            # Vertical path
            pygame.draw.rect(surface, path_color, 
                           (block_x + block_w//2 - path_width//2, block_y, 
                            path_width, block_h))
            
            # Add some trees (small green circles)
            num_trees = random.randint(5, 15)
            for _ in range(num_trees):
                tree_x = block_x + random.randint(20, block_w - 20)
                tree_y = block_y + random.randint(20, block_h - 20)
                tree_radius = random.randint(5, 10)
                
                # Skip if too close to paths
                if (abs(tree_y - (block_y + block_h//2)) < path_width or 
                    abs(tree_x - (block_x + block_w//2)) < path_width):
                    continue
                    
                tree_color = (30, 100, 30)  # Dark green
                pygame.draw.circle(surface, tree_color, (tree_x, tree_y), tree_radius)
                
                # Tree trunk
                trunk_color = (80, 50, 30)  # Brown
                pygame.draw.circle(surface, trunk_color, (tree_x, tree_y), tree_radius//2)
        
        elif block_type == "parking":
            # Create a parking lot
            lot_color = (80, 80, 80)  # Slightly lighter than roads
            pygame.draw.rect(surface, lot_color, (block_x, block_y, block_w, block_h))
            
            # Add parking lines
            line_color = (220, 220, 220)  # White
            line_spacing = 24  # Space between parking lines
            line_width = 3
            line_length = 15
            
            # Horizontal parking lines
            for y in range(block_y + 10, block_y + block_h - 10, line_spacing):
                for x in range(block_x + 10, block_x + block_w - 10, 40):
                    pygame.draw.rect(surface, line_color, (x, y, line_length, line_width))
        
        elif block_type == "special":
            # Special buildings (larger) like malls, police stations, etc.
            margin = 40
            special_color = random.choice([
                (200, 50, 50),     # Red (fire station)
                (50, 50, 180),     # Blue (police)
                (180, 180, 50),    # Yellow (mall)
                (80, 140, 180),    # Light blue (hospital)
                (120, 50, 120),    # Purple (entertainment)
            ])
            
            special_rect = pygame.Rect(
                block_x + margin, 
                block_y + margin, 
                block_w - 2*margin, 
                block_h - 2*margin
            )
            
            pygame.draw.rect(surface, special_color, special_rect)
            building_rects.append(special_rect)
            
            # Add details (special markings)
            if special_color == (80, 140, 180):  # Hospital
                # Add a white H
                h_width = min(block_w, block_h) // 5
                h_height = min(block_w, block_h) // 3
                h_x = block_x + block_w//2 - h_width//2
                h_y = block_y + block_h//2 - h_height//2
                
                pygame.draw.rect(surface, (255, 255, 255), 
                               (h_x, h_y, h_width, h_height//3))  # Horizontal bar
                pygame.draw.rect(surface, (255, 255, 255), 
                               (h_x + h_width//3, h_y, h_width//3, h_height))  # Vertical bar
            
            elif special_color == (50, 50, 180):  # Police
                # Add police markings
                pygame.draw.rect(surface, (255, 255, 255), 
                               (block_x + block_w//2 - 20, block_y + block_h//2 - 5, 40, 10))
    
    # 5. Add water bodies (blue areas) sometimes cutting across blocks
    num_water_features = random.randint(1, 3)
    for _ in range(num_water_features):
        water_x = random.randint(0, width - 400)
        water_y = random.randint(0, height - 300)
        water_width = random.randint(300, 600)
        water_height = random.randint(150, 300)
        
        water_color = (50, 100, 200)  # Blue
        water_rect = pygame.Rect(water_x, water_y, water_width, water_height)
        pygame.draw.rect(surface, water_color, water_rect)
        
        # Add shoreline
        shore_color = (200, 180, 130)  # Sandy color
        shore_width = 8
        pygame.draw.rect(surface, shore_color, 
                       (water_x - shore_width, water_y - shore_width, 
                       water_width + 2*shore_width, water_height + 2*shore_width), 
                       shore_width)
        
        # Add building collision for water
        building_rects.append(water_rect)
    
    return surface, building_rects

def add_building_details(surface, building_rect, base_color):
    """Add windows and details to buildings"""
    # Lighten color for windows
    window_color = (min(base_color[0] + 30, 255), 
                   min(base_color[1] + 30, 255), 
                   min(base_color[2] + 50, 255))
    
    # Window parameters
    window_margin = 10
    window_size = 6
    window_spacing = 14
    
    # Add windows in rows and columns
    for y in range(building_rect.top + window_margin, 
                  building_rect.bottom - window_margin, 
                  window_spacing):
        for x in range(building_rect.left + window_margin, 
                      building_rect.right - window_margin, 
                      window_spacing):
            # Skip some windows randomly
            if random.random() < 0.2:
                continue
                
            pygame.draw.rect(surface, window_color, 
                           (x, y, window_size, window_size))

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
