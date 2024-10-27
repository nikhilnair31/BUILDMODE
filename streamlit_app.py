import re
import time
import asyncio
import streamlit as st
from urllib.parse import quote_plus
from db import (
    database_init, 
    database_select_vec, 
    database_select_tweet_w_id,
    database_select_github_user
)
from api import (
    replicate_init, 
    replicate_embedding, 
    anthropic_init, 
    anthropic_chat
)
from helper import (
    serialize_f32,
    save_session_state,
    load_session_state
)
from scrape_twitter import scrape_twitter_func
from scrape_github import scrape_github_func
from start_embeddings import set_embdedding_func

messages = []
system = f"""
    You are BUILDMODE, an advanced ideation and product development assistant specializing in guiding creators through their building journey, whether it's video games, apps, AI startups, or other digital products.

    Tasks:
    - Analyze the user's social media post content to understand their interests 
    - Transform patterns in these posts into creative product opportunities
    - Utilize the user's Github profile and repositories to identify their skillset and experience

    When Ideating:
    - Always directly reference the exact social media posts that inspire the ideas proposed. Input format of social posts is (ID, POST_CONTENT, POST_IMAGE_URLS) so return the IDs of the inspiration posts. 
    - Present exactly 1 unique concept that align with their posts and interests
    - Include market potential and potential challenges for each suggestion

    Communication Style:
    - Use relevant examples and case studies
    - Ask clarifying questions when needed
    - Respond in markdown format
"""

con, cur = database_init()
replicate_client = replicate_init()

# Define a function for the chat interface (default page)
def chat_page():
    st.title("BUILDMODE")

    with st.sidebar:
        st.radio(
            "Pick the LLM model",
            ["Anthropic", "OpenAI"]
        )
        count = st.slider("How many posts to reference?", 10, 200, 100)
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "What do you want to BUILD today?"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if query := st.chat_input():
        if "api_keys" not in st.session_state:
            st.info("Please add your API key to continue.")
            st.stop()
        
        input_dict = {"modality": "text", "text_input": query}
        query_vec = replicate_embedding(replicate_client, input_dict)
        query_vec_serialized = [serialize_f32(query_vec)]
        
        similar_tweets_rows = database_select_vec(cur, query_vec_serialized, count)
        github_user_rows = database_select_github_user(cur)

        anthropic_client = anthropic_init(st.session_state["api_keys"]["anthropic_api_key"])
        st.session_state.messages.append({
            "role": "user", 
            "content": f'''
                User's Social Media Posts:
                {str(similar_tweets_rows)}

                User's Github Profile and Repositories:
                {str(github_user_rows)}

                User's Query:
                {query}
            '''
        })
        st.chat_message("user").write(query)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            with st.spinner('Thinking...'):
                response = anthropic_chat(
                    client = anthropic_client, 
                    messages = st.session_state.messages,
                    system = system, 
                )
                st.session_state.messages.append({"role": "assistant", "content": response})
                assistant_response = response

                for chunk in assistant_response.split(" "):
                    full_response += chunk + " "
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.03)
                    message_placeholder.markdown(full_response)

            pattern = r"\b\d{19}\b"
            matches = re.findall(pattern, full_response)
            columns = st.columns(len(matches), vertical_alignment="bottom")

            for idx, match in enumerate(matches):
                post_data = database_select_tweet_w_id(cur, match)
                post_url, post_text = post_data

                with columns[idx]:
                    if post_url != "-":
                        post_urls = post_url.split(" | ")
                        for post_url in post_urls:
                            st.link_button("Go to post", post_url)
                    else:
                        formatted_post_text = quote_plus(post_text)
                        google_search_url = f'https://www.google.com/search?q=site:x.com+{formatted_post_text}'
                        st.link_button("Go to post", google_search_url)

# Define a function for the Scraping page
def scraping_page():
    st.title("SCRAPE")

    sync_github = st.button("Sync GitHub")
    if sync_github:
        scrape_github_func(con, cur)

    sync_twitter = st.button("Sync Twitter")
    if sync_twitter:
        asyncio.run(scrape_twitter_func(con, cur))
        # scraping_to_update_data_wo_media()

    load_data = st.button("Load Data")
    if load_data:
        set_embdedding_func(replicate_client, con, cur)

# Define a function for the API keys input page
def settings_page():
    st.title("SETTINGS")
    
    load_session_state()
    save_session_state()

    # Save API keys in session state
    if "api_keys" not in st.session_state:
        st.session_state["api_keys"] = {"anthropic_api_key": "", "openai_key": ""}
    
    # Initialize missing keys in the dictionary (if any)
    if "anthropic_api_key" not in st.session_state["api_keys"]:
        st.session_state["api_keys"]["anthropic_api_key"] = ""
    if "openai_key" not in st.session_state["api_keys"]:
        st.session_state["api_keys"]["openai_key"] = ""
    
    # Input fields for API keys
    st.session_state["api_keys"]["anthropic_api_key"] = st.text_input(
        "Anthropic API Key", value=st.session_state["api_keys"]["anthropic_api_key"],
        type = "password"
    )
    st.session_state["api_keys"]["openai_key"] = st.text_input(
        "OpenAI API Key", value=st.session_state["api_keys"]["openai_key"],
        type = "password"
    )
    
    # Save button
    if st.button("Save"):
        st.success("API keys saved!")
        save_session_state()

# App name and icon
st.set_page_config(
    page_title="BUILDMODE",
    page_icon="⚙️",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "[Github](https://github.com/nikhilnair31/BUILDMODE)"
    }
)

# Navigation pages
pg = st.navigation([
    st.Page(
        chat_page,
        title = "BUILDMODE",
        icon = "🤖"
    ),
    st.Page(
        scraping_page,
        title = "SCRAPE",
        icon = "🔎"
    ),
    st.Page(
        settings_page,
        title = "SETTINGS",
        icon = "⚙️"
    ),
])
pg.run()