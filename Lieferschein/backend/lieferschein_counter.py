"""
Lieferschein counter management
Maintains a persistent counter for Lieferschein numbers
"""

import os
import json
from typing import Optional

COUNTER_FILE = os.path.join(os.path.dirname(__file__), '.lieferschein_counter.json')
START_NUMBER = 900  # Starting from DZ2025-0900

def get_next_lieferschein_number() -> str:
    """Get the next Lieferschein number in sequence"""
    # Read current counter
    current_number = START_NUMBER
    
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, 'r') as f:
                data = json.load(f)
                current_number = data.get('last_number', START_NUMBER)
        except:
            pass
    
    # Increment for next number
    next_number = current_number + 1
    
    # Save new counter
    try:
        with open(COUNTER_FILE, 'w') as f:
            json.dump({'last_number': next_number}, f)
    except:
        pass
    
    return f"DZ2025-{next_number:04d}"

def get_current_number() -> int:
    """Get the current counter number without incrementing"""
    current_number = START_NUMBER
    
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, 'r') as f:
                data = json.load(f)
                current_number = data.get('last_number', START_NUMBER)
        except:
            pass
    
    return current_number

def reset_counter(start_from: Optional[int] = None):
    """Reset the counter to a specific number or back to start"""
    reset_to = (start_from - 1) if start_from else (START_NUMBER - 1)
    
    with open(COUNTER_FILE, 'w') as f:
        json.dump({'last_number': reset_to}, f)