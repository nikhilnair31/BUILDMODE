import os
import json
import pickle
import struct
import streamlit as st
from typing import List
from dotenv import load_dotenv

load_dotenv()

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

def save_session_state():
    file_path = os.getenv('SAVE_PATH')

    # Ensure the directory for SAVE_PATH exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write the session state to the file
    with open(file_path, 'wb') as f:
        pickle.dump(st.session_state.to_dict(), f)

def load_session_state():
    file_path = os.getenv('SAVE_PATH')

    # Check if the file exists, if not, create it with empty session data
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        save_session_state()  # Create the file with the current session state

    # Load session state from file
    try:
        with open(file_path, 'rb') as f:
            loaded_state = pickle.load(f)
            for k, v in loaded_state.items():
                st.session_state[k] = v
    except EOFError:
        print("File is empty or corrupted.")