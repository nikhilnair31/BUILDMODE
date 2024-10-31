import re
import time
import json
import asyncio
import streamlit as st
from PIL import Image
from typing import List
from scrape_twitter import scrape_twitter_func
from scrape_github import scrape_github_func
from start_embeddings import set_embdedding_func
from saving import (
    update_env_file
)
from ui import (
    create_sync_section,
    create_link_buttons
)
from db import (
    database_init, 
    database_select_vec, 
    database_select_tweet_w_id,
    database_select_github_user
)
from api import (
    replicate_embedding, 
    anthropic_chat,
    openai_chat,
    openai_func_call
)
from helper import (
    serialize_f32,
    encode_image_to_base64
)

con, cur = database_init()

def init_sys():
    base_system = f"""
        You are BUILDMODE, an advanced ideation and product development assistant specializing in guiding creators through their building journey, whether it's video games, apps, AI startups, or other digital products.

        Tasks:
        - Analyze the user's social media post content to understand their interests 
        - Transform patterns in these posts into creative product opportunities
        - Utilize the user's Github profile and repositories to identify their skillset and experience

        When Ideating:
        - Always directly reference the exact social media posts that inspire the ideas proposed. Input format of social posts is (ID, POST_CONTENT, POST_IMAGE_URLS) so return the IDs of the inspiration posts. 
        - Present exactly top 3 unique concept that align with their posts and interests
        - Provide a single paragraph for each idea then elaborate if the user needs more details
        - Include market potential and potential challenges for each suggestion

        Communication Style:
        - Use relevant examples and case studies
        - Ask clarifying questions when needed
        - Respond in markdown format
    """
    github_user_rows = database_select_github_user(cur)
    system_prompt = f'''
        {base_system}

        User's Github Profile and Repositories:
        {str(github_user_rows)}
    '''
    return system_prompt

# Define a function for the chat interface (default page)
def chat_page():
    st.title("BUILDMODE")

    count = 100
    llm_provider = "Anthropic"
    system_prompt = init_sys()

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "What do you want to BUILD today?"}
        ]

    # Loop to display chat
    for msg in st.session_state.messages:
        # For system messages do not display the content
        if msg["role"] == "system":
            continue
        
        # For user messages, extract only the query part
        display_content = msg["content"]
        if msg["role"] == "user":
            display_content = display_content.split("User's Query: ")[-1]
        st.chat_message(msg["role"]).write(display_content)

    if chatinput := st.chat_input(accept_file=True, file_type=["png", "jpg"]):
        # Pull text and image from user's chat input
        user_input_text = chatinput.text
        user_input_files = chatinput.files

        # Use function call to check if user's asking for an idea
        similar_tweets_rows = []
        response = openai_func_call(user_input_text)
        tool_call = response.choices[0].message.tool_calls
        if tool_call:
            tool_query = json.loads(tool_call[0].function.arguments).get('user_input_text')
            query_vec = replicate_embedding(
                "daanelson/imagebind:0383f62e173dc821ec52663ed22a076d9c970549c209666ac3db181618b7a304",
                {"modality": "text", "text_input": tool_query}
            )
            query_vec_serialized = [serialize_f32(query_vec)]
            similar_tweets_rows = database_select_vec(cur, query_vec_serialized, count)

        # FIXME: Need to pass these images into the api
        # Encode image to base64
        image_base64s = []
        if user_input_files:
            for uploaded_file in user_input_files:
                image = Image.open(uploaded_file)
                image_base64 = encode_image_to_base64(image)
                image_base64s.append(image_base64)

        # Save messages to session state
        st.session_state.messages.append({
            "role": "user", 
            "content": [
                f"Relevant Social Media Posts: {str(similar_tweets_rows)}\nUser's Query: {user_input_text}"
            ]
        })
        st.chat_message("user").write(user_input_text)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner('Thinking...'):
                response = anthropic_chat(
                    model="claude-3-5-sonnet-20241022",
                    images=similar_tweets_rows,
                    messages=st.session_state.messages,
                    system=system_prompt
                ) if llm_provider == "Anthropic" else openai_chat(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages,
                    system=system_prompt
                )
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                assistant_response = response
                full_response = ""
                for chunk in assistant_response.split(" "):
                    full_response += chunk + " "
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.03)
                    message_placeholder.markdown(full_response)

            # Extracting tweet IDs from a list of tweet IDs and generating link buttons 
            matches = re.findall(r"\b\d{19}\b", full_response)
            if matches:
                columns = st.columns(len(matches), vertical_alignment="bottom")
                for idx, match in enumerate(matches):
                    post_data = database_select_tweet_w_id(cur, match)
                    create_link_buttons(col = columns[idx], data = post_data)

# Define a function for the Scraping page
def settings_page():
    st.title("SETTINGS")
    
    create_sync_section(
        "GitHub Settings", 
        [
            [
                ("Username", "GITHUB_USERNAME", "text"), 
                ("Access Token", "GITHUB_ACCESS_TOKEN", "password")
            ]
        ]
    )
    github_sync_btn = st.button("Sync", key="sync_github")
    if github_sync_btn:
        github_stop_btn = st.button("Stop")
        scrape_github_func(con, cur)
        if github_stop_btn:
            github_sync_btn.disabled = False
            st.stop()

    st.divider()

    create_sync_section(
        "Twitter Settings", 
        [
            [
                ("Twitter Screen Name", "USER_SCREEN_NAME", "text"), 
                ("Twitter Username", "USERNAME", "text")
            ],
            [
                ("Twitter Email", "EMAIL", "text"), 
                ("Twitter Password", "PASSWORD", "password")
            ],
            [(
                "Twitter Rate Limit", "TWITTER_RATE_LIMIT", ("number", 10)), 
                ("Twitter Reset Interval", "TWITTER_RESET_INTERVAL", ("number", 20))
            ]
    ])
    twitter_sync_btn = st.button("Sync", key="sync_twitter")
    if twitter_sync_btn:
        twitter_stop_btn = st.button("Stop")
        scrape_twitter_func(con, cur)
        if twitter_stop_btn:
            twitter_sync_btn.disabled = False
            st.stop()

    st.divider()

    create_sync_section(
        "LLM Settings", 
        [
            [
                ("Anthropic API Key", "ANTHROPIC_API_KEY", "password")
            ],
            [
                ("OpenAI API Key", "OPENAI_API_KEY", "password")
            ],
            [
                ("Replicate API Key", "REPLICATE_API_KEY", "password")
            ]
        ]
    )
    embeddings_sync_btn = st.button("Sync", key="sync_embeddings")
    if embeddings_sync_btn:
        embeddings_stop_btn = st.button("Stop")
        set_embdedding_func(con, cur)
        if embeddings_stop_btn:
            embeddings_sync_btn.disabled = False
            st.stop()

    st.divider()

    if st.button("Save", type="primary"):
        if update_env_file():
            st.success("Settings saved successfully!")
        else:
            st.error("Failed to save settings. Please check the error message above.")

# Set the page configuration
st.set_page_config(
    page_title="BUILDMODE",
    page_icon=":material/build:",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "[Github](https://github.com/nikhilnair31/BUILDMODE)"
    }
)
pg = st.navigation([
    st.Page(
        chat_page,
        title = "BUILDMODE",
        icon = "🤖"
    ),
    st.Page(
        settings_page,
        title = "SETTINGS",
        icon = "⚙️"
    ),
])
pg.run()