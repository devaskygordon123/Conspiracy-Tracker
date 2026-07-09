import feedparser
import requests
import json
import os
import re
from datetime import datetime

# 1. THE PLACES WE LISTEN TO
rss_feeds = [
    "https://www.reddit.com/r/conspiracy/new/.rss",
    "https://www.reddit.com/r/conspiracy_commons/new/.rss",
    "https://www.reddit.com/r/QAnon_Casualties/new/.rss",
    "https://www.reddit.com/r/TrueOffMyChest/new/.rss",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCa6QWHlA2uMmU5B5vMuT5Pw",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCsQalatfFKkvjSv-T7j9Mug",
    "https://www.zerohedge.com/fullrss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

def gather_rss_clues():
    clues = []
    for url in rss_feeds:
        try:
            feed = feedparser.parse(url, request_kwargs={'timeout': 10})
            for item in feed.entries[:5]: # Reduced to 5 posts to be extra safe
                title = getattr(item, 'title', 'No title')
                desc = getattr(item, 'description', 'No description')
                clues.append(title + " " + desc[:100]) # Reduced to 100 characters
        except:
            pass 
    return clues

def gather_4chan_clues():
    clues = []
    boards = ['x', 'pol']
    for board in boards:
        try:
            res = requests.get(f"https://a.4cdn.org/{board}/catalog.json", timeout=10)
            pages = res.json()
            for page in pages[:1]:
                for thread in page['threads'][:5]: 
                    sub = thread.get('sub', '')
                    com = thread.get('com', '')
                    com = re.sub('<[^>]+>', '', com)[:100] # Reduced to 100 characters
                    clues.append(f"4chan /{board}/: {sub} {com}")
        except:
            pass 
    return clues

def ask_cloud_ai_brain_both_questions(clues):
    if not clues:
        return "The robot couldn't hear any gossip today.", "The robot couldn't hear any gossip today."
        
    today_date = datetime.now().strftime("%B %d")
    
    # We ask BOTH questions in ONE letter!
    prompt = f"""
    You are a conspiracy analyst robot. Look at these short internet posts from 4chan, Reddit, and YouTube:
    {clues}
    
    Today's date is {today_date}.
    
    I need you to do TWO things:
    1. Find ONLY brand new conspiracy theories being discussed for the first time. Ignore old conspiracies unless there is a new twist today.
    2. Find OLD conspiracies, past predictions, or historical theories mentioned today, OR predictions specifically pointing to today's date ({today_date}).
    
    You MUST output your answer EXACTLY in this format:
    ===NEW===
    [Bulleted list of new conspiracies, or "None today."]
    ===PAST===
    [Bulleted list of past/dated conspiracies, or "None today."]
    """
    
    api_key = os.environ.get("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code != 200:
            error_msg = f"Error: {response.text}"
            return error_msg, error_msg
        
        ai_thoughts = response.json()['choices'][0]['message']['content']
        
        # Split the AI's answer into two sections
        if "===PAST===" in ai_thoughts:
            parts = ai_thoughts.split("===PAST===")
            new_section = parts[0].replace("===NEW===", "").strip()
            past_section = parts[1].strip()
            return new_section, past_section
        else:
            return ai_thoughts, "Error parsing time machine section."
            
        try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code != 200:
            error_msg = f"Error: {response.text}"
            return error_msg, error_msg
        
        ai_thoughts = response.json()['choices'][0]['message']['content']
        
        # ROBOT DECODER RING! Looks for the secret split code
        if "===PAST===" in ai_thoughts:
            parts = ai_thoughts.split("===PAST===")
            new_section = parts[0].replace("===NEW===", "").strip()
            past_section = parts[1].strip()
            return new_section, past_section
        elif "===NEW===" in ai_thoughts:
            # If the AI only wrote the NEW code but forgot PAST
            new_section = ai_thoughts.replace("===NEW===", "").strip()
            return new_section, "None today."
        else:
            # If the AI forgot the secret code completely, just put it all in NEW
            return ai_thoughts, "None today."
            
    except Exception as e:
        error_msg = f"Connection broke: {str(e)}"
        return error_msg, error_msg

def save_to_notebook(new_response, past_response):
    today_data = {
        "conspiracies": new_response,
        "past_conspiracies": past_response
    }
    with open("data.json", "w") as file:
        json.dump(today_data, file)
    print("Robot Detective finished updating both notebooks!")

# RUN THE DETECTIVE
print("Gathering clues...")
rss_clues = gather_rss_clues()
chan_clues = gather_4chan_clues()
all_clues = rss_clues + chan_clues

print("Asking AI brain to do both tasks at once...")
new_thoughts, past_thoughts = ask_cloud_ai_brain_both_questions(all_clues)

save_to_notebook(new_thoughts, past_thoughts)
