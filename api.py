import os
import replicate
import anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

REPLICATE_API_KEY = os.getenv('REPLICATE_API_KEY')

#region Replicate

# Initialize Replicate client
def replicate_init():
    client = replicate.Client(
        api_token = REPLICATE_API_KEY
    )
    
    return client

# Generate Replicate embedding
def replicate_embedding(client, input_dict):
    output_embedding_vec = client.run(
        "daanelson/imagebind:0383f62e173dc821ec52663ed22a076d9c970549c209666ac3db181618b7a304",
        input = input_dict
    )
    
    return output_embedding_vec

#endregion

#region OpenAI

# Initialize OpenAI client
def openai_init(llm_api_key):
    client = OpenAI(
        api_key = llm_api_key
    )
    
    return client

# Generate OpenAI embedding
def openai_embedding():
    response = client.embeddings.create(
        input="Your text string goes here",
        model="text-embedding-3-small"
    )
    
    embedding = response.data[0].embedding
    print(f'embedding: {embedding}')

    return embedding

# Generate OpenAI chat completion
def openai_chat(client, model, messages):
    # Build the parameters dictionary
    params = {
        "model": model,
        "max_tokens": 8192,
        "temperature": 1,
        "messages": messages
    }

    completion = client.chat.completions.create(**params)
    response = completion.choices[0].message.content

    return response

#endregion

#region Anthropic

# Initialize Anthropic client
def anthropic_init(llm_api_key):
    client = anthropic.Anthropic(
        api_key =  llm_api_key
    )
    
    return client

# Generate Anthropic chat completion
def anthropic_chat(client, messages, system = None):
    # Build the parameters dictionary dynamically
    params = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 8192,
        "temperature": 1,
        "messages": messages
    }
    
    # Only include 'system' if it's provided
    if system is not None:
        params["system"] = system

    completion = client.messages.create(**params)
    response = completion.content[0].text
    
    return response

#endregion