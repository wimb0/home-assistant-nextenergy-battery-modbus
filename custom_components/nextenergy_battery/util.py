"""Utility functions for the NextEnergy Battery integration."""
from typing import Dict

def parse_bitfield_messages(value: int | None, message_map: Dict[int, str]) -> str:
    """Parse a bitfield value and return a comma-separated string of messages."""
    if value is None or value == 0:
        return "OK"
    
    active_messages = []
    # Loop through all 16 possible bits
    for bit in range(16):
        # Check if the bit is active in the value
        if (value >> bit) & 1:
            # If we have a known message for this bit, add it
            if bit in message_map:
                active_messages.append(message_map[bit])
            # Otherwise, report the unknown active bit
            else:
                active_messages.append(f"Reserved bit {bit}")
            
    if not active_messages:
        # This case should technically not be reached if value is not 0, but as a fallback
        return "Unknown State"
        
    return ", ".join(active_messages)
