import re
from urllib.parse import quote_plus
from db import database_init, database_select_tweet_w_id

con, cur = database_init()

text = f'''
    Based on your social media posts and GitHub activity, I can see you have a strong interest in game development, particularly in unique combat mechanics, physics-based gameplay, and roguelite elements. Let me propose 3 concepts that align with your experience in C# and Unity/Unreal while incorporating your interest in absurd shooter mechanics.

    1. "Solar Surfer" - Physics-Based Solar Roguelite
    Inspired by posts: 1776042931054432438, 1847835596569350340

    Concept:

    Play as a tiny maintenance robot surfing on solar flares using physics-based movement
    Use the sun's plasma as both weapon and movement mechanic - surf on waves, redirect solar flares at enemies
    Each run has you diving deeper into the sun's layers, with different physics properties and hazards
    Market Potential:

    Unique setting differentiates from typical space/sci-fi roguelites
    Physics-based gameplay appeals to fans of games like Totally Accurate Battle Simulator
    Could tap into both roguelite and physics puzzle game markets
    Challenges:

    Complex physics system needs careful balancing
    Visual clarity in an all-bright environment
    Performance optimization for particle effects
    2. "Helios Heist" - Tactical Sun-Based Combat
    Inspired by posts: 1812192143429013566, 1756511109702422899

    Concept:

    You're a space bandit stealing energy from the sun
    Use solar-powered weapons that overheat intentionally for critical hits
    Each run involves managing heat levels - weapons become more powerful but more unstable as they heat up
    Random equipment malfunctions create chaotic moments
    Market Potential:

    Appeals to fans of risk/reward gameplay mechanics
    Humorous take on serious sci-fi setting
    Room for interesting weapon/equipment combinations
    Challenges:

    Balancing risk/reward mechanics
    Making heat management fun rather than tedious
    Designing varied content for multiple runs
    3. "Corona Corps" - Co-op Sun Defense
    Inspired by posts: 1810342787025367389, 1831819479908823372

    Concept:

    Defend solar collection stations from waves of sun-dwelling creatures
    Each player controls a different specialized mech with unique cooling systems
    Roguelite progression through unlocking new mech parts and cooling methods
    Absurd twist: enemies are sentient solar flares wearing tiny hats
    Market Potential:

    Co-op roguelites have proven popular (Risk of Rain 2, Gunfire Reborn)
    Silly aesthetic could build community through memes/clips
    Room for cosmetic DLC and regular content updates
    Challenges:

    Networking complexity for co-op play
    Balancing for both solo and multiplayer
    Creating enough enemy variety
    Based on your GitHub profile showing strong C# experience and game development projects like GLITCH, any of these concepts would be within your technical capabilities while pushing into new creative territory. The physics-based "Solar Surfer" might be particularly interesting given your experience with combat systems and particle effects.

    Would you like me to elaborate on any of these concepts or discuss specific technical implementation approaches?
'''
pattern = r"\b\d{19}\b"
matches = re.findall(pattern, text)

for match in matches:
    post_data = database_select_tweet_w_id(cur, match)
    print(f'post_data: {post_data}')
    post_url, post_text = post_data

    if post_url != "-":
        post_urls = post_url.split(" | ")
        for post_url in post_urls:
            print(f'post_url: {post_url}')
    else:
        formatted_post_text = quote_plus(post_text)
        google_search_url = f'https://www.google.com/search?q=site:x.com+{formatted_post_text}'
        print(f'google_search_url: {google_search_url}')