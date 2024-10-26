import asyncio
import streamlit as st
from db import (
    database_init, 
    database_select_vec, 
    database_select_github_user
)
from api import (
    replicate_init, 
    replicate_embedding, 
    anthropic_init, 
    anthropic_chat
)
from helper import serialize_f32
from scrape_twitter import scrape_twitter_func
from scrape_github import scrape_github_func
from start_embeddings import set_embdedding_func

messages = []
system = f"""
    You are BUILDMODE, an advanced ideation and product development assistant specializing in guiding creators through their building journey, whether it's video games, apps, AI startups, or other digital products.

    Primary Mission: IDEATION SPECIALIST

    Analyze user's social media content to understand their interests, expertise, and potential
    Transform patterns in their content into creative product opportunities
    Maintain an encouraging, collaborative tone as their ideation partner

    When Ideating:

    Always start by highlighting specific references from their social media that inspire ideas and provide the ID for the post
    Present exactly 3 unique concepts that align with their demonstrated interests
    Frame each idea in an exciting, actionable way: "Based on your posts about X, you could build Y"
    Include market potential for each suggestion
    Note potential challenges and solutions

    Key Approaches:

    Ideation Phase:
    Distill complex information into clear, high-potential concepts
    Focus on innovation gaps and market opportunities
    Consider technical feasibility and resource requirements

    Development Support:
    Break down large projects into manageable milestones
    Suggest specific tools and technologies
    Provide risk assessment and mitigation strategies

    Market Intelligence:
    Analyze competitor landscapes
    Identify target audience segments
    Track relevant industry trends
    Evaluate monetization strategies

    Communication Style:
    Use relevant examples and case studies
    Ask clarifying questions when needed
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
        
        system_context = system
        if len(st.session_state.messages) == 1:
            input_dict = {"modality": "text", "text_input": query}
            query_vec = replicate_embedding(replicate_client, input_dict)
            query_vec_serialized = [serialize_f32(query_vec)]
            
            similar_tweets_rows = database_select_vec(cur, query_vec_serialized, count)
            github_user_rows = database_select_github_user(cur)
            system_context += f'''
                User's Github Profile and Repos Data:
                {str(github_user_rows)}

                User's Social Media Content:
                {str(similar_tweets_rows)}
            '''
            # print(f'system_context\n{system_context}')

        anthropic_client = anthropic_init(st.session_state["api_keys"]["anthropic_api_key"])
        st.session_state.messages.append({"role": "user", "content": query})
        st.chat_message("user").write(query)
        response = anthropic_chat(
            client = anthropic_client, 
            messages = st.session_state.messages,
            system = system_context, 
        )
        st.session_state.messages.append({"role": "assistant", "content": response})
        assistant_msg = st.chat_message("assistant")
        assistant_msg.markdown(response)

        #TODO: Figure out how to pull URL from response
        assistant_msg.link_button("Go to post", "https://x.com/i/bookmarks")

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