import subprocess
import os
import time
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_environment():
    """Validate and set required environment variables"""
    # Check for display environment variable
    display_env = os.getenv('DISPLAY', ':0')
    sdl_video_driver = os.getenv('SDL_VIDEODRIVER', 'x11')
    
    logging.info(f"Current environment: DISPLAY={display_env}, SDL_VIDEODRIVER={sdl_video_driver}")
    
    if display_env != ':0':
        logging.warning("DISPLAY environment variable is not set to :0, setting it now")
    
    if sdl_video_driver != 'x11':
        logging.warning("SDL_VIDEODRIVER environment variable is not set to x11, setting it now")
    
    # Set the environment variables
    os.environ['DISPLAY'] = ':0'
    os.environ['SDL_VIDEODRIVER'] = 'x11'
    
    logging.info(f"Environment variables set: DISPLAY={os.environ['DISPLAY']}, SDL_VIDEODRIVER={os.environ['SDL_VIDEODRIVER']}")

def check_pygame_installation():
    """Check if pygame is properly installed"""
    try:
        import pygame
        pygame_version = pygame.version.ver
        logging.info(f"Pygame version: {pygame_version}")
        return True
    except ImportError:
        logging.error("Pygame not installed or not found in Python path")
        return False
    except Exception as e:
        logging.error(f"Error checking pygame: {e}")
        return False

def start_game():
    """Start the game in VNC mode"""
    logging.info("Starting game in VNC mode...")
    
    # Validate environment
    validate_environment()
    
    # Check pygame
    if not check_pygame_installation():
        logging.error("Cannot start game: pygame issue detected")
        return
    
    # Start the game in the foreground
    try:
        logging.info("Launching main.py...")
        process = subprocess.Popen(['python', 'main.py'], 
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 text=True,
                                 env=os.environ.copy())  # Explicitly pass environment
        
        # Show output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                logging.debug(output.strip())
                
        # Check exit code
        exit_code = process.poll()
        logging.info(f"Game exited with code: {exit_code}")
        
    except Exception as e:
        logging.error(f"Error starting game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set up environment for VNC
    logging.info("Setting up VNC environment...")
    start_game()