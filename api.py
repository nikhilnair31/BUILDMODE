import os
import json
import replicate
import anthropic
from openai import OpenAI
from dotenv import load_dotenv
from helper import serialize_clean
import streamlit as st

load_dotenv()

#region Replicate

def replicate_init():
    REPLICATE_API_KEY = os.getenv('REPLICATE_API_KEY')

    if not REPLICATE_API_KEY:
        st.error("Please add your Replicate API key to continue.")
        st.stop()

    return replicate.Client(api_token = REPLICATE_API_KEY)
def replicate_embedding(model, input_dict):
    client = replicate_init()

    output_embedding_vec = client.run(
        model,
        input = input_dict
    )
    
    return output_embedding_vec

#endregion

#region OpenAI

def openai_init():
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    if not OPENAI_API_KEY:
        st.error("Please add your OpenAI API key to continue.")
        st.stop()

    return OpenAI(api_key = OPENAI_API_KEY)
def openai_chat(model, messages, system = None):
    # Only include 'system' if it's provided
    if system is not None:
        messages.insert(0, {"role": "system", "content": system})

    # Build the parameters dictionary dynamically
    params = {
        "model": model,
        "max_tokens": 8192,
        "temperature": 1,
        "messages": messages
    }

    client = openai_init()
    completion = client.chat.completions.create(**params)
    response = completion.choices[0].message.content

    return response
def openai_func_call(query):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_relevant_tweets",
                "description": "Get the relevant tweets for the user's query. Call this whenever the user asks for something to build or wants some ideas",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {
                            "type": "string",
                            "description": "The user's query",
                        },
                    },
                    "required": ["query_text"],
                    "additionalProperties": False,
                },
            }
        }
    ]

    params = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Use the supplied tools to assist the user."},
            {"role": "user", "content": query}
        ],
        "tools":tools,
    }

    client = openai_init()
    response = client.chat.completions.create(**params)
    
    return response

#endregion

#region Anthropic

def anthropic_init():
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    if not ANTHROPIC_API_KEY:
        st.error("Please add your Anthropic API key to continue.")
        st.stop()

    return anthropic.Anthropic(api_key = ANTHROPIC_API_KEY)
def anthropic_chat(model, messages, system = None):
    # Build the parameters dictionary dynamically
    params = {
        "model": model,
        "max_tokens": 8192,
        "temperature": 1,
        "messages": messages
    }
    
    # Only include 'system' if it's provided
    if system is not None:
        params["system"] = system

    client = anthropic_init()
    completion = client.messages.create(**params)
    response = completion.content[0].text
    
    return response

#endregion