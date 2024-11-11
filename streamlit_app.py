import re
import os
import time
import json
import asyncio
import threading
import streamlit as st
from PIL import Image
from typing import List
from datetime import datetime
from scrape_twitter import (
    scrape_twitter_func
)
from scrape_github import (
    scrape_github_func
)
from start_embeddings import (
    set_embdedding_func,
    get_avg_vec
)
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
    get_system_prompt,
    replicate_embedding, 
    anthropic_chat,
    openai_chat,
    openai_func_call,
    openrouter_chat
)
from helper import (
    serialize_f32,
    encode_image_to_base64
)

con, cur = database_init()
github_user_rows = database_select_github_user(cur)
system_prompt = get_system_prompt(github_user_rows)

class ConversationManager:
    def __init__(self, save_dir="conversations"):
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
    def save_conversation(self, conversation, thread_id):
        filename = f"{self.save_dir}/conversation_{thread_id}.json"
        with open(filename, 'w') as f:
            json.dump(conversation, f)
            
    def load_conversation(self, thread_id):
        filename = f"{self.save_dir}/conversation_{thread_id}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return []
    
    def list_conversations(self):
        files = os.listdir(self.save_dir)
        threads = []
        for file in files:
            if file.startswith('conversation_') and file.endswith('.json'):
                thread_id = file.replace('conversation_', '').replace('.json', '')
                threads.append(thread_id)
        return sorted(threads, reverse=True)  # Most recent first
    
    def delete_conversation(self, thread_id):
        filename = f"{self.save_dir}/conversation_{thread_id}.json"
        if os.path.exists(filename):
            os.remove(filename)

    def create_new_thread(self):
        thread_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_conversation(
            [
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": "What do you want to BUILD today?"}
            ], 
            thread_id
        )
        return thread_id

def initialize_session_state():
    if 'conversation_manager' not in st.session_state:
        st.session_state.conversation_manager = ConversationManager()
    
    if 'current_thread' not in st.session_state:
        threads = st.session_state.conversation_manager.list_conversations()
        if threads:
            st.session_state.current_thread = threads[0]  # Load most recent
        else:
            st.session_state.current_thread = st.session_state.conversation_manager.create_new_thread()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = st.session_state.conversation_manager.load_conversation(
            st.session_state.current_thread
        )

def format_messages(provider, text_content, image_contents):
    if provider == "Anthropic":
        formatted_images = [{
            "type": "image",
            "source": {
                "type": image.type,
                "media_type": image.media_type,
                "data": image.data
            }
        } for image in image_contents]
        
        formatted_text = {
            "type": "text",
            "text": text_content["text"]
        }
        
        return [formatted_text] + formatted_images
    elif provider == "OpenAI":
        content = []
        content.append(text_content)
        
        for image in image_contents:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image.media_type};base64,{image.data}"
                }
            })
            
        return [{"role": "user", "content": content}]
    else:
        user_content = [text_content] + image_contents
    
    return user_content

def process_user_input(llm_provider, user_input_text, user_input_files):
    # Use function call to check if user's asking for an idea
    similar_tweets_rows = []
    response = openai_func_call(user_input_text)
    tool_call = response.choices[0].message.tool_calls
    print(f'tool_call: {tool_call}')
    if tool_call:
        tool_query = json.loads(tool_call[0].function.arguments).get('query_text')
        # FIXME: Use the input image with the text to pull relevant content
        query_vec = replicate_embedding(
            "daanelson/imagebind:0383f62e173dc821ec52663ed22a076d9c970549c209666ac3db181618b7a304",
            {"modality": "text", "text_input": tool_query}
        )
        query_vec_serialized = [serialize_f32(query_vec)]
        similar_tweets_rows = database_select_vec(cur, query_vec_serialized, count)
    
    text_content_dic = {
        "type": "text",
        "text": f"""
            <social_media_posts>
            {str(similar_tweets_rows)}
            </social_media_posts>
            
            <user_query>
            {user_input_text}
            </user_query>
        """,
    }

    # Encode image to base64
    image_contents_list = []
    if user_input_files:
        for uploaded_file in user_input_files:
            image = Image.open(uploaded_file)
            base64_image = encode_image_to_base64(image)
            image_contents_list.append(base64_image)
    
    return {
        "role": "user", 
        "content": format_messages(llm_provider, text_content_dic, image_contents_list)
    }

def generate_link(cur, text):
    matches = re.findall(r"\b\d{19}\b", text)
    if matches:
        columns = st.columns(len(matches), vertical_alignment="bottom")
        for idx, match in enumerate(matches):
            post_data = database_select_tweet_w_id(cur, match)
            create_link_buttons(col = columns[idx], data = post_data)
            
def stream_text(text):
    message_placeholder = st.empty()
    full_response = ""
    for chunk in text.split(" "):
        full_response += chunk + " "
        message_placeholder.markdown(full_response + "▌")
        time.sleep(0.03)
        message_placeholder.markdown(full_response)

# Define a function for the chat interface (default page)
def chat_page():
    st.title("BUILDMODE")

    count = 100
    llm_provider = "Anthropic"

    with st.sidebar:
        # Button to start new conversation
        if st.button("New Conversation"):
            thread_id = st.session_state.conversation_manager.create_new_thread()
            st.session_state.current_thread = thread_id
            st.session_state.messages = []
            st.rerun()
        
        # List existing conversations
        threads = st.session_state.conversation_manager.list_conversations()
        for conv_id, conv_thread in enumerate(threads):
            # print(f'conv_thread: {conv_thread} | conv_id: {conv_id}')
            
            # Add date formatting for better readability
            display_date = datetime.strptime(conv_thread, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M")
            
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"Conv: {display_date}", key=conv_thread):
                    st.session_state.current_thread = conv_thread
                    st.session_state.messages = st.session_state.conversation_manager.load_conversation(conv_thread)
                    st.rerun()
            with col2:
                if st.button('🗑️', key=f'delete_{conv_id}'):
                    st.session_state.conversation_manager.delete_conversation(conv_thread)
                    # If we're deleting the current thread, switch to the most recent one
                    if conv_thread == st.session_state.current_thread:
                        remaining_threads = st.session_state.conversation_manager.list_conversations()
                        if remaining_threads:
                            st.session_state.current_thread = remaining_threads[0]
                            st.session_state.messages = st.session_state.conversation_manager.load_conversation(remaining_threads[0])
                        else:
                            # If no conversations left, create a new one
                            new_thread = st.session_state.conversation_manager.create_new_thread()
                            st.session_state.current_thread = new_thread
                            st.session_state.messages = []
                    st.rerun()
                 
    # Create a container for the chat messages and Loop to display chat
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            # For system messages do not display the content
            if msg["role"] == "system":
                continue
            
            # For user messages, extract only the query part
            if msg["role"] == "user":
                display_content = msg["content"][0]["text"]
                display_content = display_content.split("<user_query>")[1]
                display_content = display_content.replace("</user_query>", "")
                print(f'user display_content: {display_content}')
                st.chat_message("user").write(display_content)
            
            # For user messages, extract only the query part
            # TODO: Make this work in case the LLM API sends back an image
            if msg["role"] == "assistant":
                display_content = msg["content"]
                st.chat_message("assistant").write(display_content)
                generate_link(cur, display_content)

    if chatinput := st.chat_input(accept_file=True, file_type=["png"]):
        # Pull text and image from user's chat input
        user_input_text = chatinput.text
        user_input_files = chatinput.files

        # Process user input
        user_content = process_user_input(llm_provider, user_input_text, user_input_files)

        # Save messages to session state
        st.session_state.messages.append(user_content)
        st.session_state.conversation_manager.save_conversation(
            st.session_state.messages,
            st.session_state.current_thread
        )

        # Display user input
        with chat_container:
            with st.chat_message("user"):
                if user_input_files:
                    for uploaded_file in user_input_files:
                        st.image(uploaded_file)
                st.write(user_input_text)
        
        # Display assistant response
        with chat_container:
            with st.chat_message("assistant"):
                assistant_response = openrouter_chat(
                    provider=llm_provider,
                    model="anthropic/claude-3.5-sonnet:beta",
                    messages=st.session_state.messages
                )
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": assistant_response
                })
                
                # Emulate streaming response from LLM API
                stream_text(assistant_response)

                # Extracting tweet IDs from a list of tweet IDs and generating link buttons 
                generate_link(cur, assistant_response)

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

    # Sync button to start syncing process in a new conv_thread
    if st.button("Sync", key="sync_twitter"):
        if st.session_state.syncing_twitter:
            st.warning("Sync already in progress!")
        else:
            st.session_state.syncing_twitter = True
            st.session_state.sync_thread = threading.conv_Thread(target=scrape_twitter_func, args=(con, cur))
            st.session_state.sync_thread.start()
            st.success("Sync started!")

    # Stop button to stop syncing process
    if st.button("Stop", key="stop_twitter"):
        if st.session_state.syncing_twitter:
            st.session_state.syncing_twitter = False
            st.success("Sync stopped.")
        else:
            st.warning("No sync in progress.")

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

def main():
    initialize_session_state()

    pg = st.navigation([
        st.Page(
            chat_page,
            title="BUILDMODE",
            icon="⚙️"
        ),
        st.Page(
            settings_page,
            title="Settings",
            icon="⚙️"
        ),
    ])
    pg.run()

if __name__ == "__main__":
    main()