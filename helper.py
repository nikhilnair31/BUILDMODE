import os
import json
import struct
from typing import List

# Serializes a list of floats into a compact "raw bytes" format
def serialize_f32(vector: List[float]) -> bytes:
    return struct.pack("%sf" % len(vector), *vector)

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