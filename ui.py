import streamlit as st
from urllib.parse import quote_plus
from db import (
    database_select_tweet_w_id
)

def create_sync_section(title, inputs):
    st.header(title)
    for row in inputs:
        cols = st.columns(len(row), vertical_alignment="bottom")
        for col, (label, key, input_type) in zip(cols, row):
            if input_type == "text":
                col.text_input(label)
            elif input_type == "password":
                col.text_input(label, type="password")
            elif input_type == "number":
                col.number_input(label, value=input_type[1])
        
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
                google_search_url = f'https://www.google.com/search?q=site:x.com+{formatted_post_text}'
                st.link_button(label="", icon=":material/open_in_new:", url=google_search_url)
    else:
        return