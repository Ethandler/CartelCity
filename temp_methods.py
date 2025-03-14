def generate_roads_from_grid_pattern(self):
    """Create road segments for AI navigation based on a grid pattern similar to GTA"""
    # This method is called when using the procedural map generator
    # It creates road segments that vehicles can follow
    
    # If roads are already defined, keep them
    if hasattr(self, 'roads') and self.roads:
        print(f"Using existing {len(self.roads)} road segments")
        return
        
    # Initialize roads list if not already done
    if not hasattr(self, 'roads'):
        self.roads = []
        
    # GTA-style city parameters
    block_size = 320  # Same as in procedural map generator
    road_width = 120  # Width of roads
    
    # Create horizontal roads
    for y in range(road_width // 2, self.height, block_size):
        # Skip if too close to edge
        if y >= self.height - road_width // 2:
            continue
            
        # Add a complete road from left to right
        self.roads.append({
            "rect": pygame.Rect(0, y - road_width // 2, self.width, road_width),
            "horizontal": True
        })
    
    # Create vertical roads
    for x in range(road_width // 2, self.width, block_size):
        # Skip if too close to edge
        if x >= self.width - road_width // 2:
            continue
            
        # Add a complete road from top to bottom
        self.roads.append({
            "rect": pygame.Rect(x - road_width // 2, 0, road_width, self.height),
            "horizontal": False
        })
        
    print(f"Generated {len(self.roads)} road segments for AI navigation")