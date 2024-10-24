from api import replicate_init, replicate_embedding, openai_init, openai_chat, anthropic_init, anthropic_chat
from db import database_init
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
anthropic_client = anthropic_init()
replicate_client = replicate_init()

def get_query_context(query_vec):
    global system

    rows = cur.execute(
        """
        SELECT T.ID, T.FULL_TEXT, T.MEDIA_URL_HTTPSS_STR
        FROM TWEETS T
        INNER JOIN (
            SELECT ID
            FROM VECS
            WHERE EMBEDDING MATCH ? AND K = 100
            ORDER BY DISTANCE ASC
        ) V
        ON T.ID = V.ID
        """,
        [serialize_f32(query_vec)],
    ).fetchall()
    # print_select_rows(rows)

    system += str(rows)

    return system

def conversation_loop():
    global system, messages
    
    while True:
        # Get user input for the conversation
        query = input(f"YOU\n")
        
        if query.lower() in ['terminate']:
            print("Ending conversation.")
            break

        system_context  = system
        if len(messages) == 0:
            input_dict = {"modality": "text", "text_input": query}
            query_vec = replicate_embedding(replicate_client, input_dict)
            system_context = get_query_context(query_vec)
        
        # Append user message to chat history
        user_message = {
            "role": "user",
            "content": query
        }
        messages.append(user_message)
        
        # Fetch response from Anthropic API
        response = anthropic_chat(anthropic_client, system_context, messages)
        
        if response:
            # Append assistant's response to chat history
            assistant_message = {
                "role": "assistant",
                "content": response
            }
            messages.append(assistant_message)

if __name__ == "__main__":
    print("Starting chat... (type 'exit' to stop)")
    conversation_loop()