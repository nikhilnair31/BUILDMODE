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
    client = OpenAI(OPEN_AI_API_KEY)
    
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
