import os
import pickle
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from typing import Dict, Any, List, Tuple, Union

load_dotenv()

# Global dictionary to store all input values
if 'env_input_values' not in st.session_state:
    st.session_state.env_input_values = {}

def load_env_value(key, default=None):
    try:
        value = os.getenv(key)
        return value if value is not None else default
    except Exception as e:
        st.warning(f"Error loading value for {key}: {str(e)}")
        return default

def set_key(dotenv_path: str, key: str, value: str) -> None:
    """Write or update an environment variable in the .env file."""
    try:
        with open(dotenv_path, 'r') as file:
            lines = file.readlines()

        # Find if key exists
        key_exists = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                key_exists = True
                break

        # If key doesn't exist, append it
        if not key_exists:
            lines.append(f"{key}={value}\n")

        # Write back to file
        with open(dotenv_path, 'w') as file:
            file.writelines(lines)
    except Exception as e:
        raise Exception(f"Error setting key {key}: {str(e)}")

def update_env_file() -> bool:
    """Update .env file with values from session state."""
    try:
        # Find or create .env file
        dotenv_path = find_dotenv()
        if not dotenv_path:
            dotenv_path = os.path.join(os.getcwd(), '.env')
            with open(dotenv_path, 'w') as f:
                pass
        
        # Collect all input values from session state
        env_updates: Dict[str, str] = {}
        for key in st.session_state:
            value = st.session_state[key]
            if value is not None:
                # Convert value to string if it's not already
                str_value = str(value)
                env_updates[key] = str_value
                
        # Update .env file
        for key, value in env_updates.items():
            set_key(dotenv_path, key, value)
            # Update os.environ to reflect changes immediately
            os.environ[key] = value

        # Reload environment variables
        load_dotenv(override=True)
        return True
        
    except Exception as e:
        st.error(f"Error updating .env file: {str(e)}")
        return False