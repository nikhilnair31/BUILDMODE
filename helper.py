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