import streamlit as st
from urllib.parse import quote_plus
from db import (
    database_select_tweet_w_id
)
from saving import (
    load_env_value
)

def create_sync_section(title, inputs):
    st.header(title)
    
    for row in inputs:
        cols = st.columns(len(row), vertical_alignment="bottom")
        for col, input_config in zip(cols, row):
            # Unpack input configuration
            if len(input_config) == 3:
                label, env_key, input_type = input_config
                default_value = None
            else:
                label, env_key, input_type, default_value = input_config
                
            # Load value from .env
            env_value = load_env_value(env_key, default_value)
            st.session_state[env_key] = env_value
            
            # Create appropriate input widget based on type
            if input_type == "text":
                col.text_input(label, value=env_value, key=env_key)
            elif input_type == "password":
                col.text_input(label, value=env_value, type="password", key=env_key)
            elif input_type == "number":
                try:
                    # Convert env_value to int if it exists
                    numeric_value = int(env_value) if env_value is not None else 0
                    col.number_input(label, value=numeric_value, key=env_key)
                except ValueError:
                    st.warning(f"Invalid number format for {env_key} in .env file")
                    col.number_input(label, value=0.0, key=env_key)

# TODO: Add a twitter icon for links
def create_link_buttons(col, data):
    if data:
        post_url, post_text = data
        with col:
            if post_url != "-":
                post_urls = post_url.split(" | ")
                for post_url in post_urls:
                    st.link_button(label="", icon=":material/open_in_new:", url=post_url)
            else:
                formatted_post_text = quote_plus(post_text)
                search_url = f'https://x.com/search?q={formatted_post_text}'
                st.link_button(label="", icon=":material/open_in_new:", url=search_url)
    else:
        return