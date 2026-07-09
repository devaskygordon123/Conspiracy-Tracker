import feedparser
import requests
import json
import os
import re
import time
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
            for item in feed.entries[:15]: 
                title = getattr(item, 'title', 'No title')
                desc = getattr(item, 'description', 'No description')
                clues.append(title + " " + desc[:300]) 
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
                for thread in page['threads'][:10]: 
                    sub = thread.get('sub', '')
                    com = thread.get('com', '')
                    com = re.sub('<[^>]+>', '', com)[:300]
                    clues.append(f"4chan /{board}/: {sub} {com}")
        except:
            pass 
    return clues

def ask_ai_for_chunk(chunk, today_date):
    """Reads a small chapter of papers and writes a deep report."""
    prompt = f"""
    You are an expert, in-depth conspiracy analyst robot. Look at these internet posts from 4chan, Reddit, YouTube, and News:
    {chunk}
    
    Today's date is {today_date}.
    
    I need you to do TWO things with DEEP ANALYSIS:
    1. Find ONLY brand new conspiracy theories being discussed for the first time. Provide a detailed analysis of what the theory is and why people are talking about it today. Ignore old conspiracies unless there is a brand new twist today.
    2. Find OLD conspiracies, past predictions, or historical theories mentioned today, OR predictions specifically pointing to today's date ({today_date}). Explain the history of the prediction.
    
    You MUST output your answer EXACTLY in this format:
    ===NEW===
    [Bulleted list with deep analysis, or "None today."]
    ===PAST===
    [Bulleted list with deep analysis, or "None today."]
    """
    
    api_key = os.environ.get("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=45)
        if response.status_code != 200:
            return f"Error: {response.text}", "Error."
        
        ai_thoughts = response.json()['choices'][0]['message']['content']
        
        # Decoder Ring
        if "===PAST===" in ai_thoughts:
            parts = ai_thoughts.split("===PAST===")
            new_section = parts[0].replace("===NEW===", "").strip()
            past_section = parts[1].strip()
            return new_section, past_section
        elif "===NEW===" in ai_thoughts:
            new_section = ai_thoughts.replace("===NEW===", "").strip()
            return new_section, "None today."
        else:
            return ai_thoughts, "None today."
            
    except Exception as e:
        return f"Connection broke: {str(e)}", "Error."

def save_to_notebook(new_response, past_response):
    today_data = {
        "conspiracies": new_response,
        "past_conspiracies": past_response
    }
    with open("data.json", "w") as file:
        json.dump(today_data, file)
    print("Robot Detective finished updating both notebooks!")

# RUN THE DETECTIVE
print("Gathering a giant stack of clues...")
rss_clues = gather_rss_clues()
chan_clues = gather_4chan_clues()
all_clues = rss_clues + chan_clues

today_date = datetime.now().strftime("%B %d")
all_new_reports = []
all_past_reports = []

# THE CHAPTER METHOD: Cut the giant stack into chunks of 8 posts
chunk_size = 8
print(f"Total clues gathered: {len(all_clues)}. Reading in chunks of {chunk_size}...")

for i in range(0, len(all_clues), chunk_size):
    chunk = all_clues[i:i + chunk_size]
    print(f"Reading Chapter {i//chunk_size + 1}...")
    
    new_str, past_str = ask_ai_for_chunk(chunk, today_date)
    all_new_reports.append(new_str)
    all_past_reports.append(past_str)
    
    # Take a 3-second nap so the AI brain doesn't choke
    if i + chunk_size < len(all_clues):
        time.sleep(3)

# Staple all the reports together!
final_new = "\n\n".join(all_new_reports)
final_past = "\n\n".join(all_past_reports)

print("Stapling reports together and saving...")
save_to_notebook(final_new, final_past)
