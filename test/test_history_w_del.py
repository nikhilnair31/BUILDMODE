import os
import json
import streamlit as st

def load_conversations():
    """Load existing conversations from the JSON file"""
    if os.path.exists('conversations.json'):
        with open('conversations.json', 'r') as f:
            return json.load(f)
    return {}

def save_conversations(conversations):
    """Save conversations to the JSON file"""
    with open('conversations.json', 'w') as f:
        json.dump(conversations, f, indent=4)

def delete_conversation(conversation_id, conversations):
    """Delete a specific conversation and return updated conversations"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        save_conversations(conversations)
    return conversations

def display_conversations():
    """Display saved conversations with delete buttons"""
    conversations = load_conversations()
    
    if not conversations:
        st.info("No saved conversations found.")
        return None
    
    st.subheader("Saved Conversations")
    
    for conv_id, conv_data in conversations.items():
        col1, col2, col3 = st.columns([3, 1, 0.5])
        
        with col1:
            # Display conversation title or first message
            title = conv_data.get('title', conv_data['messages'][0]['content'][:50] + '...')
            st.write(f"**{title}**")
        
        with col2:
            # Load conversation button
            if st.button('Load', key=f'load_{conv_id}'):
                return conv_data['messages']
        
        with col3:
            # Delete conversation button
            if st.button('🗑️', key=f'delete_{conv_id}'):
                conversations = delete_conversation(conv_id, conversations)
                st.rerun()  # Refresh the page to show updated list
    
    return None

# Example usage in your main app:
def main():
    st.title("Chat Application")
    
    # Initialize session state for messages if not exists
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display saved conversations with delete functionality
    loaded_messages = display_conversations()
    
    # If a conversation was loaded, update the session state
    if loaded_messages is not None:
        st.session_state.messages = loaded_messages
        st.rerun()  # Refresh to show loaded conversation
    
if __name__ == "__main__":
    main()