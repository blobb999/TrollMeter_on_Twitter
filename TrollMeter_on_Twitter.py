#This code is a GUI application that scrapes tweets from a Twitter user and analyses the text of the tweets to determine 
#if they contain aggressive language, and whether or not they are troll posts. The application uses snscrape to scrape the tweets, 
#and then performs various calculations on the text to determine the aggressiveness score of the tweet, and whether or not it is a troll post. 
#The results are displayed in a CSV file and a detailed troll score window. The GUI was built using the tkinter library, 
#and the code is organized into a class called TrollMeterGUI. The GUI allows the user to enter a Twitter username, 
#select the number of tweets to scrape, and start the scraping process. Once the process is complete, the GUI displays
#a detailed troll score window that shows the number of tweets that were scraped, the number of troll posts, and the percentage
#of troll posts. The window also includes a barometer that displays the percentage of troll posts graphically.
#
#For combiling this Project you need:
#pip install pyinstaller==4.5.1 using Python up to version 3.10.x. 
#According to the PyInstaller documentation, support for Python 3.11 is currently experimental and may not work correctly for the snscrape module.
#pyinstaller --onefile --upx-dir=\upx TrollMeter_on_Twitter.py

import tkinter as tk
from tkinter import Canvas
import snscrape.modules.twitter as sntwitter
import pandas as pd
import constants
import pyperclip
import re
import math
from datetime import datetime

def fetch_user_creation_date(username):
    user = next(sntwitter.TwitterUserScraper(username).get_items())
    return user.user.created

class TrollMeterGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        # Define 'var' attribute
        self.var = tk.StringVar(value="50")

        # Call the create_widgets method
        self.create_widgets()

    def create_widgets(self):
        # Create username entry and label
        self.username_label = tk.Label(self.master, text="Enter Twitter username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack()

        # Create start button
        self.start_button = tk.Button(self.master, text="Start", command=self.start_scraping)
        self.start_button.pack()

        # Create custom amount label and entry
        self.custom_amount_label = tk.Label(self.master, text="Enter a custom amount of tweets to scrape (optional):")
        self.custom_amount_label.pack()
        self.custom_amount_entry = tk.Entry(self.master)
        self.custom_amount_entry.pack()

        # Create max tweets dropdown menu
        self.max_tweets_label = tk.Label(self.master, text="Select max number of tweets to scrape:")
        self.max_tweets_label.pack()
        self.tweet_options = ["50", "100", "all"]
        self.var.set(self.tweet_options[0])
        self.max_tweets_dropdown = tk.OptionMenu(self.master, self.var, *self.tweet_options)
        self.max_tweets_dropdown.pack()

    def start_scraping(self):
        # Get username
        username = self.username_entry.get()
        username = re.sub(r'\W+', '', username)

        # Use snscrape to scrape data and append tweets to list
        tweets_list = []
        max_tweets = None

        # Determine max number of tweets to scrape
        if self.var.get() == "all":
            max_tweets = None
        elif self.custom_amount_entry.get().isdigit():
            max_tweets = int(self.custom_amount_entry.get())
        else:
            max_tweets = int(self.var.get())

        # Display status update
        self.status_label = tk.Label(self.master, text="Scraping in progress...")
        self.status_label.pack()
        self.master.update()

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f"from:{username}").get_items()):
            if max_tweets is not None and i >= max_tweets:
                break

            # Calculate scores
            text = tweet.rawContent.lower()
            aggressiveness_score, aggressiveness_counts, is_contra_account, contains_contra_topic = self.calculate_scores(text, tweet)

            # Determine if tweet is a troll post
            is_troll = False
            if aggressiveness_score >= 1 and not (is_contra_account and contains_contra_topic):
                is_troll = True

            # Add tweet data to list
            tweets_list.append((tweet.date, tweet.id, tweet.rawContent, tweet.url, aggressiveness_counts, is_troll))

            # Update status label
            self.status_label.config(text=f"Scraped {i+1} tweets...")
            self.master.update()

        # Remove status label
        self.status_label.pack_forget()

        # Create dataframe from list
        tweets_df = pd.DataFrame(tweets_list, columns=["Date", "ID", "Content", "URL", "Aggressiveness Counts", "Troll"])

        # Filter by number of tweets if specified
        if max_tweets is not None:
            tweets_df = tweets_df.head(max_tweets)

        # Save the results to a CSV file
        self.save_to_csv(tweets_df, username)

        # Display detailed score
        self.show_detailed_troll_score(tweets_df)

    def save_to_csv(self, tweets_df, username):
        # Filter by Troll status
        troll_tweets_df = tweets_df[tweets_df['Troll'] == True]

        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create filename with username and timestamp
        filename = f"{username}_{timestamp}.csv"

        # Save troll tweets to CSV file
        troll_tweets_df.to_csv(filename, index=False)


    def calculate_scores(self, text, tweet):
        # Initialize scores
        pro_score = 0
        contra_score = 0
        sentinel_score = 0
        aggressiveness_counts = {}
        contra_topic_counts = {}

        # Check each word in the text
        for word in text.split():
            lower_word = word.lower()

            if lower_word in constants.AGGRESSIVENESS_WORDS:
                aggressiveness_counts[lower_word] = aggressiveness_counts.get(lower_word, 0) + constants.AGGRESSIVENESS_WORDS[lower_word]

            if lower_word in constants.PRO_ACCOUNTS:
                pro_score += constants.PRO_ACCOUNTS[lower_word]
                for sentinel_word in constants.SENTINEL_WORDS:
                        sentinel_score += 1
            if lower_word in constants.CONTRA_ACCOUNTS:
                contra_score += constants.CONTRA_ACCOUNTS[lower_word]
            if lower_word in constants.SENTINEL_WORDS:
                sentinel_score += constants.SENTINEL_WORDS[lower_word]

        # Check if the tweet is from a PRO_ACCOUNTS user or contains a PRO_ACCOUNTS user's mention
        is_pro_account = tweet.user.username.lower() in constants.PRO_ACCOUNTS or any(user.lower() in text for user in constants.PRO_ACCOUNTS)
        is_contra_account = tweet.user.username.lower() in constants.CONTRA_ACCOUNTS or any(user.lower() in text for user in constants.CONTRA_ACCOUNTS)
        
        # Check if the tweet contains CONTRA_TOPICS and is from a CONTRA_ACCOUNTS user
        contains_contra_topic = False
        for topic in constants.CONTRA_TOPICS:
            if re.search(r'\b(?:-)?' + re.escape(topic.lower()) + r'(?:-)?\b', text):
                contains_contra_topic = True
                break

        # Check if the tweet contains CONTRA_TOPICS
        for topic in constants.CONTRA_TOPICS:
            if re.search(r'\b(?:-)?' + re.escape(topic.lower()) + r'(?:-)?\b', text):
                if is_pro_account:
                    contra_score += 1  # Increment contra_score if it is a PRO_ACCOUNT user
                else:
                    pro_score += 1     # Increment pro_score if it is not a PRO_ACCOUNT user

        # Check if the tweet contains PRO_TOPICS and SENTINEL_WORDS
        if is_pro_account:
            for topic in constants.PRO_TOPICS:
                if re.search(r'\b(?:-)?' + re.escape(topic.lower()) + r'(?:-)?\b', text):
                    pro_score += 1
            for topic in constants.SENTINEL_WORDS:
                if re.search(r'\b(?:-)?' + re.escape(topic.lower()) + r'(?:-)?\b', text):
                    pro_score += 1

        # Calculate final aggressiveness score
        aggressiveness_score = max(pro_score - contra_score, 0) + sentinel_score + sum(aggressiveness_counts.values())
        aggressiveness_score = max(aggressiveness_score, 0)

        # Add CONTRA_TOPICS counts to the aggressiveness_counts dictionary
        for topic in constants.CONTRA_TOPICS:
            topic_key = topic.lower()
            topic_count = len(re.findall(r'\b(?:-)?' + re.escape(topic_key) + r'(?:-)?\b', text))
            if topic_count > 0:
                if topic_key in aggressiveness_counts:
                    aggressiveness_counts[topic_key] += topic_count
                else:
                    aggressiveness_counts[topic_key] = topic_count

        return aggressiveness_score, aggressiveness_counts, is_contra_account, contains_contra_topic

    def show_detailed_troll_score(self, tweets_df):
        troll_count = len(tweets_df[tweets_df['Troll'] == True])
        total_tweets = len(tweets_df)
        troll_percentage = (troll_count / total_tweets) * 100

        # Create a new window to display the detailed troll score
        troll_window = tk.Toplevel(self.master)
        troll_window.title("Troll Score Details")

        # Add a top header in the GUI with "Troll Score"
        troll_score_header = tk.Label(troll_window, text="Troll Score", font=("Helvetica", 30, "bold"))
        troll_score_header.pack()

        # Add Username, Creation Date, and Age labels
        username = self.username_entry.get()
        user_creation_date = fetch_user_creation_date(username)
        age_days = (pd.Timestamp.utcnow() - user_creation_date).days

        username_label = tk.Label(troll_window, text=f"Username: {username}")
        username_label.pack()
        creation_date_label = tk.Label(troll_window, text=f"Creation Date: {user_creation_date.strftime('%Y-%m-%d')}")
        creation_date_label.pack()
        age_label = tk.Label(troll_window, text=f"Age: {age_days} days")
        age_label.pack()

        troll_label = tk.Label(troll_window, text=f"Scanned Tweets: {total_tweets}")
        troll_label.pack()

        troll_label = tk.Label(troll_window, text=f"Troll Tweets: {troll_count}")
        troll_label.pack()

        troll_label = tk.Label(troll_window, text=f"Troll Percentage: {troll_percentage:.2f}%")
        troll_label.pack()

        # Create canvas for barometer
        canvas = tk.Canvas(troll_window, width=200, height=100)
        canvas.pack()

        # Draw barometer
        self.draw_barometer(canvas, troll_percentage)

        troll_tweets = tweets_df[tweets_df['Troll'] == True]

        # Consolidate 'Aggressiveness Counts' for each keyword
        consolidated_counts = {}
        for _, row in troll_tweets.iterrows():
            aggressiveness_counts = row['Aggressiveness Counts']
            for key, value in aggressiveness_counts.items():
                if key in consolidated_counts:
                    consolidated_counts[key] += value
                else:
                    consolidated_counts[key] = value

        # Display consolidated 'Aggressiveness Counts'
        for key, value in consolidated_counts.items():
            count_label = tk.Label(troll_window, text=f"{key}: {value}")
            count_label.pack()


    def draw_barometer(self, canvas, percentage):
        # Draw gradient circle
        for i in range(360):
            angle = 360 - i
            color = self.calculate_color(angle)
            x1, y1 = self.calculate_point_on_circle(100, 100, 90, angle)
            x2, y2 = self.calculate_point_on_circle(100, 100, 90, angle + 1)
            canvas.create_arc(10, 10, 190, 190, start=angle - 90, extent=1, outline=color, width=5)

        # Calculate needle angle
        angle = (180 * (percentage / 100)) - 180

        # Calculate needle end point
        x2 = 100 + 80 * math.cos(math.radians(angle))
        y2 = 100 + 80 * math.sin(math.radians(angle))

        # Draw needle
        canvas.create_line(100, 100, x2, y2, fill="black", width=2)

        # Draw center circle
        canvas.create_oval(95, 95, 105, 105, fill="black")

    def calculate_color(self, angle):
        r = int(255 * (1 - angle / 360))
        g = int(255 * angle / 360)
        return f'#{r:02x}{g:02x}00'

    def calculate_point_on_circle(self, cx, cy, r, angle):
        x = cx + r * math.cos(math.radians(angle))
        y = cy + r * math.sin(math.radians(angle))
        return x, y

root = tk.Tk()
root.title("Twitter Troll Meter")
gui = TrollMeterGUI(root)
root.mainloop()
