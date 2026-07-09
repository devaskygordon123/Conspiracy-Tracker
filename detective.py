import feedparser
import requests
import json
import os

# 1. THE PLACES WE LISTEN TO (We added News sites and more forums!)
rss_feeds = [
    # Reddit Conspiracy Boards
    "https://www.reddit.com/r/conspiracy/new/.rss",
    "https://www.reddit.com/r/conspiracy_commons/new/.rss",
    "https://www.reddit.com/r/QAnon_Casualties/new/.rss",
    "https://www.reddit.com/r/TrueOffMyChest/new/.rss",
    "https://www.reddit.com/r/wayfair/new/.rss",
    # Mainstream News (Sometimes conspiracies start here)
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
]

def gather_clues():
    """Reads the internet tickertape and grabs the text."""
    clues = []
    for url in rss_feeds:
        try:
            feed = feedparser.parse(url)
            # WE CHANGED THIS FROM 10 TO 25! Grabs more posts.
            for item in feed.entries[:25]: 
                title = getattr(item, 'title', 'No title')
                desc = getattr(item, 'description', 'No description')
                clues.append(title + " " + desc)
        except Exception:
            pass # If one feed fails, just skip it!
    return clues

def ask_cloud_ai_brain(clues):
    if not clues:
        return "The robot couldn't hear any gossip from the internet today (Reddit might be blocking the server). Try again tomorrow!"
        
    # WE UPDATED THE RULES HERE! Now it lists EVERYTHING.
    prompt = f"""
    You are a conspiracy analyst robot. Look at these internet posts and news headlines:
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
    print(f"Saved: {ai_response}")

# RUN THE DETECTIVE
clues = gather_clues()
ai_thoughts = ask_cloud_ai_brain(clues)
save_to_notebook(ai_thoughts)
