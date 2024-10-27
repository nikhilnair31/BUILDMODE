import os
import pickle
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def init_session_state():
    st.session_state.clear()

def save_session_state():
    file_path = os.getenv('SAVE_PATH')

    # Ensure the directory for SAVE_PATH exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write the session state to the file
    with open(file_path, 'wb') as f:
        sesh_state_dict = st.session_state.to_dict()
        print(f'session state is {sesh_state_dict}')
        pickle.dump(sesh_state_dict, f)
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