import feedparser
import requests
import json
import os
import re
from datetime import datetime

# 1. THE PLACES WE LISTEN TO (Reddit, YouTube, News)
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
            feed = feedparser.parse(url)
            for item in feed.entries[:25]: 
                title = getattr(item, 'title', 'No title')
                desc = getattr(item, 'description', 'No description')
                clues.append(title + " " + desc)
        except:
            pass
    return clues

def gather_4chan_clues():
    """Reads 4chan's secret filing cabinet"""
    clues = []
    boards = ['x', 'pol'] # x is Paranormal, pol is Politics
    for board in boards:
        try:
            # 4chan's secret API link
            res = requests.get(f"https://a.4cdn.org/{board}/catalog.json")
            pages = res.json()
            for page in pages[:1]: # Just grab the first page
                for thread in page['threads'][:10]: # Top 10 threads
                    sub = thread.get('sub', '')
                    com = thread.get('com', '')
                    # Strip out HTML tags from 4chan posts
                    com = re.sub('<[^>]+>', '', com)
                    clues.append(f"4chan /{board}/: {sub} {com}")
        except:
            pass
    return clues

def ask_cloud_ai_brain(clues, is_time_machine=False):
    if not clues:
        return "The robot couldn't hear any gossip today."
        
    today_date = datetime.now().strftime("%B %d") # Gets today's Month and Day
    
    if is_time_machine:
        prompt = f"""
        You are a conspiracy time traveler robot. Look at these internet posts from 4chan, Reddit, and YouTube:
        {clues}
        
        Also, note that today's date is {today_date}.
        
        Find any OLD conspiracies, past predictions, or historical theories that are being mentioned today, OR any predictions/projections that specifically point to today's date ({today_date}).
        
        Output as a bulleted list. If there are none, say "None today."
        """
    else:
        prompt = f"""
        You are a conspiracy analyst robot. Look at these internet posts from 4chan, Reddit, and YouTube:
        {clues}
        
        Find ONLY brand new conspiracy theories being discussed for the first time.
        Ignore old conspiracies unless there is a brand new twist today.
        
        List EVERY single new conspiracy you find. Output as a bulleted list. If there are none, say "None today."
        """
    
    api_key = os.environ.get("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            return f"Error: {response.text}"
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Connection broke: {str(e)}"

def save_to_notebook(new_response, past_response):
    # Now saving TWO notebooks in one file!
    today_data = {
        "conspiracies": new_response,
        "past_conspiracies": past_response
    }
    with open("data.json", "w") as file:
        json.dump(today_data, file)
    print("Robot Detective finished updating both notebooks!")

# RUN THE DETECTIVE
print("Gathering clues from RSS and 4chan...")
rss_clues = gather_rss_clues()
chan_clues = gather_4chan_clues()
all_clues = rss_clues + chan_clues

print("Asking AI about NEW conspiracies...")
new_thoughts = ask_cloud_ai_brain(all_clues, is_time_machine=False)

print("Asking AI about PAST/DATED conspiracies...")
past_thoughts = ask_cloud_ai_brain(all_clues, is_time_machine=True)

save_to_notebook(new_thoughts, past_thoughts)
