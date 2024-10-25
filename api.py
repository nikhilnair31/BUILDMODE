import os
import replicate
import anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
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
        model = "gpt-4o",
        max_tokens = 8192,
        temperature = 0.9,
        messages = [
            {
                "role": "system", 
                "content": 
                    f"""
                    You are BUILDMODE, an advanced product development assistant specializing in guiding creators through their building journey, whether it's video games, apps, AI startups, or other digital products.
                    Core Functions:

                    Transform social media insights into actionable product ideas
                    Provide step-by-step guidance through all development stages
                    Offer data-driven market analysis and trend identification
                    Generate targeted brainstorming sessions

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
                    """
            },
            {
                "role": "user", 
                "content": 
                    f"""
                    Query: 
                    {query}

                    Content: 
                    {content}
                    """
            }
        ]
    )

    response = completion.choices[0].message
    print(
        f'-------------------------------------------------------',
        f'RESPONSE',
        f'{response}',
        f'-------------------------------------------------------',
        sep='\n'
    )

    return response

#endregion

#region Anthropic

# Initialize Anthropic client
def anthropic_init(llm_api_key):
    client = anthropic.Anthropic(
        api_key =  llm_api_key if llm_api_key else ANTHROPIC_API_KEY
    )
    
    return client

# Generate Anthropic chat completion
def anthropic_chat(client, system, messages):
    completion = client.messages.create(
        model = "claude-3-5-sonnet-20241022",
        max_tokens = 8192,
        temperature = 1,
        system = system,
        messages = messages
    )

    response = completion.content[0].text
    print(
        f'-------------------------------------------------------',
        f'RESPONSE',
        f'{response}',
        f'-------------------------------------------------------',
        sep='\n'
    )
    
    return response

#endregion