import re
import os
import random
import time

def create_safe_filename(input_string):
    # Replace any character that is not alphanumeric, a period, a hyphen, or an underscore with an underscore
    safe_filename = re.sub(r'[^\w.-]', '_', input_string)
    return safe_filename    

def sanitize_no_specialchars(text):
    """Sanitize the string to keep only alphanumeric characters and spaces, remove others."""
    return re.sub(r'[^a-zA-Z0-9 ]', '', text)

def ensure_directory(dir):
    """Ensure the directory exists, create if it does not, handle errors if creation fails."""
    try:
        os.makedirs(dir, exist_ok=True)
    except OSError as e:
        # Handle specific errors related to os.makedirs
        if not os.path.isdir(dir):
            raise RuntimeError(f"Failed to create directory {dir}: {e.strerror}") from e
        

def random_sleep(min_seconds=1, max_seconds=5):
    # Generate a random float number between min_seconds and max_seconds
    sleep_time = random.uniform(min_seconds, max_seconds)
    # Sleep for the computed time
    time.sleep(sleep_time)

