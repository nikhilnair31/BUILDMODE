import json
import struct
from typing import List

def serialize_f32(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.pack("%sf" % len(vector), *vector)

def print_select_rows(rows):
    idx = 1
    for row in rows:
        print(
            f'idx: {idx} - id: {row[0]}',
            f'text: {row[1]}',
            f'urls: {row[2]}',
            f'-------------------------------------------------------',
            sep='\n'
        )
        idx += 1

# Function to automatically remove non-serializable attributes
def serialize_clean(tweet):
    clean_data = {}
    for key, value in tweet.__dict__.items():
        try:
            # Try serializing each attribute to JSON
            json.dumps(value)
            clean_data[key] = value  # Only add it if it's serializable
        except (TypeError, OverflowError):
            pass  # Skip non-serializable fields
    return clean_data