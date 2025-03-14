import subprocess
import os
import time

def start_game():
    """Start the game in VNC mode"""
    print("Starting game in VNC mode...")
    
    # Make sure the display is set
    os.environ['DISPLAY'] = ':0'
    
    # Set full screen mode for better visibility
    os.environ['SDL_VIDEODRIVER'] = 'x11'
    
    # Start the game in the foreground
    try:
        print("Launching main.py...")
        process = subprocess.Popen(['python', 'main.py'], 
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 text=True)
        
        # Show output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                
        # Check exit code
        exit_code = process.poll()
        print(f"Game exited with code: {exit_code}")
        
    except Exception as e:
        print(f"Error starting game: {e}")

if __name__ == "__main__":
    # Set up environment for VNC
    print("Setting up VNC environment...")
    start_game()