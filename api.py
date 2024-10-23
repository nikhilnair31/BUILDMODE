import os
import replicate
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')
REPLICATE_API_KEY = os.getenv('REPLICATE_API_KEY')

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

# Initialize OpenAI client
def openai_init():
    client = OpenAI(
        api_key = OPEN_AI_API_KEY
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
def openai_chat(client, query, content):
    completion = client.chat.completions.create(
        model="gpt-4o",
        temperature = 0.9,
        messages=[
            {
                "role": "system", 
                "content": 
                    f"""
                    You are a tool called BUILDMODE. You have access to the user's saved social media posts. 
                    When a user is searching for inspiration to build something, consolidate the content to help inspire the user.
                    """
            },
            {
                "role": "user", 
                "content": 
                    f"""
                    Query: {query}

                    Content: {content}
                    """
            }
        ]
    )

    response = completion.choices[0].message
    print(f'\nresponse: {response.content}')

    return response
