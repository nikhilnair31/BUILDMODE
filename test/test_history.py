import streamlit as st
from datetime import datetime
import json
import os

# Configure Streamlit page
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    def create_new_thread(self):
        thread_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_conversation([], thread_id)
        return thread_id

    def delete_conversation(self, thread_id):
        filename = f"{self.save_dir}/conversation_{thread_id}.json"
        if os.path.exists(filename):
            os.remove(filename)

def initialize_session_state():
    # Initialize basic session state
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
    
    # Initialize settings
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'model' not in st.session_state:
        st.session_state.model = "gpt-3.5-turbo"
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7

def chat_page():
    st.title("💬 AI Chat Assistant")
    
    # Sidebar for conversation management
    with st.sidebar:
        st.header("Conversation Management")
        
        # Button to start new conversation
        if st.button("New Conversation", key="new_chat"):
            thread_id = st.session_state.conversation_manager.create_new_thread()
            st.session_state.current_thread = thread_id
            st.session_state.messages = []
            st.rerun()
        
        # List existing conversations
        st.subheader("Previous Conversations")
        threads = st.session_state.conversation_manager.list_conversations()
        for thread in threads:
            col1, col2 = st.columns([4, 1])
            display_date = datetime.strptime(thread, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M")
            
            with col1:
                if st.button(f"📝 {display_date}", key=f"load_{thread}"):
                    st.session_state.current_thread = thread
                    st.session_state.messages = st.session_state.conversation_manager.load_conversation(thread)
                    st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"delete_{thread}"):
                    st.session_state.conversation_manager.delete_conversation(thread)
                    if st.session_state.current_thread == thread:
                        # Create new thread if we deleted the current one
                        st.session_state.current_thread = st.session_state.conversation_manager.create_new_thread()
                        st.session_state.messages = []
                    st.rerun()

    # Main chat interface
    current_date = datetime.strptime(
        st.session_state.current_thread, 
        "%Y%m%d_%H%M%S"
    ).strftime("%Y-%m-%d %H:%M")
    st.subheader(f"Current Conversation: {current_date}")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Here you would integrate with your LLM API using session state settings
        response = f"Bot response to: {prompt} (using {st.session_state.model} at {st.session_state.temperature} temperature)"
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Save conversation
        st.session_state.conversation_manager.save_conversation(
            st.session_state.messages,
            st.session_state.current_thread
        )
        
        st.rerun()

def settings_page():
    pass

def main():
    initialize_session_state()
    
    # Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Chat", "Settings"])
    
    # Display the selected page
    if page == "Chat":
        chat_page()
    else:
        settings_page()

if __name__ == "__main__":
    main()