import feedparser
import requests
import json
import os

# 1. THE PLACES WE LISTEN TO (Free RSS feeds from Reddit)
rss_feeds = [
    "https://www.reddit.com/r/conspiracy/new/.rss",
    "https://www.reddit.com/r/conspiracy_commons/new/.rss",
    "https://www.reddit.com/r/QAnon_Casualties/new/.rss"
]

def gather_clues():
    clues = []
    for url in rss_feeds:
        feed = feedparser.parse(url)
        for item in feed.entries[:10]: # Grab the 10 newest posts
            clues.append(item.title + " " + item.description)
    return clues

def ask_cloud_ai_brain(clues):
    # This is the rulebook we give the AI
    prompt = f"""
    You are a conspiracy analyst robot. Look at these internet posts:
    {clues}
    
    Find ONLY brand new conspiracy theories being discussed for the first time.
    Ignore old conspiracies (like JFK, Flat Earth, or 9/11) unless there is a brand new twist today.
    
    Output the results as a simple bulleted list. If there are no new conspiracies, say "None today."
    """
    
    # We talk to the Groq Cloud Brain using our secret password
    api_key = os.environ.get("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    ai_thoughts = response.json()['choices'][0]['message']['content']
    return ai_thoughts

def save_to_notebook(ai_response):
    # Save the AI's thoughts into our digital notebook
    today_data = {"conspiracies": ai_response}
    with open("data.json", "w") as file:
        json.dump(today_data, file)
    print("Robot Detective finished updating the notebook!")

# RUN THE DETECTIVE
clues = gather_clues()
ai_thoughts = ask_cloud_ai_brain(clues)
save_to_notebook(ai_thoughts)
