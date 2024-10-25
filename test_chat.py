import streamlit as st
from db import database_init
from api import replicate_init, replicate_embedding, openai_init, openai_chat, anthropic_init, anthropic_chat
from helper import serialize_f32, print_select_rows

messages = []
system = f"""
    You are BUILDMODE, an advanced product development assistant specializing in guiding creators through their building journey, whether it's video games, apps, AI startups, or other digital products.

    Primary Mission: IDEATION SPECIALIST

    Analyze user's social media content to understand their interests, expertise, and potential
    Transform patterns in their content into creative product opportunities
    Maintain an encouraging, collaborative tone as their ideation partner

    When Ideating:

    Always start by highlighting specific references from their social media that inspire ideas and porovide the URL for the post
    Present exactly 3 product concepts that align with their demonstrated interests
    Frame each idea in an exciting, actionable way: "Based on your posts about X, you could build Y"

    Key Approaches:

    Ideation Phase:


    Distill complex information into 3 clear, high-potential concepts
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

    Adapt explanations to user's expertise level
    Provide clear, actionable steps
    Use relevant examples and case studies
    Ask clarifying questions when needed

    When providing inspiration:

    Present exactly 3 concise, unique ideas
    Include market potential for each suggestion
    Highlight technological requirements
    Note potential challenges and solutions

    Your goal is to transform ideas into viable products while maintaining a balance between innovation, feasibility, and market demand. 
    Always prioritize practical, actual, and actionable advice over theoretical concepts.

    Content:
    
"""

con, cur = database_init()
replicate_client = replicate_init()

def get_query_context(query_vec, cnt):
    global system

    rows = cur.execute(
        f"""
        SELECT T.ID, T.FULL_TEXT, T.MEDIA_URL_HTTPSS_STR
        FROM TWEETS T
        INNER JOIN (
            SELECT ID
            FROM VECS
            WHERE EMBEDDING MATCH ? AND K = {cnt}
            ORDER BY DISTANCE ASC
        ) V
        ON T.ID = V.ID
        """,
        [serialize_f32(query_vec)],
    ).fetchall()
    # print_select_rows(rows)

    system += str(rows)

    return system

#region Streamlit app layout

st.set_page_config(
    page_title="BUILDMODE",
    page_icon="⚙️",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "https://github.com/nikhilnair31/BUILDMODE"
    }
)

st.title("BUILDMODE")

with st.sidebar:
    anthropic_api_key = st.text_input("Anthropic API Key", key="chatbot_api_key", type="password")
    option = st.selectbox(
        "Pick the LLM model",
        ("gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022"),
    )
    count = st.slider("How many posts to reference?", 10, 200, 100)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "What do you want to BUILD today?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if query := st.chat_input():
    if not anthropic_api_key:
        st.info("Please add your Anthropic API key to continue.")
        st.stop()
    
    system_context = system
    if len(st.session_state.messages) == 1:
        input_dict = {"modality": "text", "text_input": query}
        query_vec = replicate_embedding(replicate_client, input_dict)
        system_context = get_query_context(query_vec, 100)

    anthropic_client = anthropic_init(anthropic_api_key)
    st.session_state.messages.append({"role": "user", "content": query})
    st.chat_message("user").write(query)
    response = anthropic_chat(
        anthropic_client, 
        system_context, 
        st.session_state.messages
    )
    st.session_state.messages.append({"role": "assistant", "content": response})
    assistant_msg = st.chat_message("assistant")
    assistant_msg.markdown(response)
    assistant_msg.link_button("Go to post", url)

#endregion