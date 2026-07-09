import feedparser
import requests
import json
import os

# 1. THE PLACES WE LISTEN TO (Now with YouTube and Forums!)
rss_feeds = [
    # --- REDDIT ---
    "https://www.reddit.com/r/conspiracy/new/.rss",
    "https://www.reddit.com/r/conspiracy_commons/new/.rss",
    "https://www.reddit.com/r/QAnon_Casualties/new/.rss",
    "https://www.reddit.com/r/TrueOffMyChest/new/.rss",
    
    # --- YOUTUBE (We use the secret RSS links for specific channels) ---
    # Corbett Report (Alternative news/conspiracies)
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCa6QWHlA2uMmU5B5vMuT5Pw",
    # Alltime Conspiracies
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCiE_m7qL4QRBwDJLnN4ZB7A",
    # Bright Insight (Alternative history/theories)
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCsQalatfFKkvjSv-T7j9Mug",
    
    # --- ALTERNATIVE FORUMS & NEWS ---
    # ZeroHedge (Popular alternative finance/conspiracy site)
    "https://www.zerohedge.com/fullrss.xml",
    # Gab's general trending feed (Free speech alternative platform)
    "https://trends.gab.com/feed/rss",
    # BBC World News (To catch mainstream stories that spark conspiracies)
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

def gather_clues():
    """Reads the internet tickertape and grabs the text."""
    clues = []
    for url in rss_feeds:
        try:
            feed = feedparser.parse(url)
            for item in feed.entries[:25]: 
                # YouTube RSS uses 'title' and 'link', so we grab those
                title = getattr(item, 'title', 'No title')
                desc = getattr(item, 'description', 'No description')
                clues.append(title + " " + desc)
        except Exception:
            pass # If one feed fails, just skip it!
    return clues

def ask_cloud_ai_brain(clues):
    if not clues:
        return "The robot couldn't hear any gossip from the internet today. Try again tomorrow!"
        
    prompt = f"""
    You are a conspiracy analyst robot. Look at these internet posts, YouTube video titles, and news headlines:
    {clues}
    
    Find ONLY brand new conspiracy theories being discussed for the first time.
    Ignore old conspiracies (like JFK, Flat Earth, or 9/11) unless there is a brand new twist today.
    
    IMPORTANT: List EVERY single new conspiracy you find. Do not limit it to 5. Do not summarize. 
    Output the results as a bulleted list. If there are no new conspiracies, say "None today."
    """
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Error: The robot couldn't find its secret password (API Key) in the GitHub vault."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            return f"The AI brain sent back an error. Code: {response.status_code}. Message: {response.text}"
        
        ai_thoughts = response.json()['choices'][0]['message']['content']
        return ai_thoughts
    except Exception as e:
        return f"The robot's connection to the AI brain broke: {str(e)}"

def save_to_notebook(ai_response):
    today_data = {"conspiracies": ai_response}
    with open("data.json", "w") as file:
        json.dump(today_data, file)
    print("Robot Detective finished updating the notebook!")

# RUN THE DETECTIVE
clues = gather_clues()
ai_thoughts = ask_cloud_ai_brain(clues)
save_to_notebook(ai_thoughts)
