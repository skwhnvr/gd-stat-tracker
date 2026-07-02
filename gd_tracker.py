import os
import csv
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
from zoneinfo import ZoneInfo 

# --- CONFIGURATION ---
TARGET_USERNAME = "skyewhenever"
CSV_FILE = "gd_rank_history.csv"
GRAPH_FILE = "index.html"
# ---------------------

def fetch_gd_rank(username):
    url = f"https://gdbrowser.com/api/profile/{username}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            print(f"GDBrowser API error: Status code {response.status_code}")
            return None
            
        data = response.json()
        rank = data.get("rank", 0)
        
        if rank == 0:
            print("Profile fetched, but no global rank found on this account.")
            return None
            
        return int(rank)
    except Exception as e:
        print(f"Network error trying to fetch player profile: {e}")
        return None

def log_to_csv(rank):
    uk_tz = ZoneInfo("Europe/London")
    date_str = datetime.now(uk_tz).strftime("%Y-%m-%d")
    
    rows = []
    updated = False

    if os.path.isfile(CSV_FILE):
        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
            reader = list(csv.reader(file))
            if reader:
                header = reader[0]
                for row in reader[1:]:
                    if row:
                        if row[0] == date_str:
                            row[1] = str(rank)
                            updated = True
                        rows.append(row)
            else:
                header = ["Date", "Leaderboard Position"]
    else:
        header = ["Date", "Leaderboard Position"]

    if not updated:
        rows.append([date_str, rank])

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Successfully logged rank {rank} for date {date_str}")

def generate_graph():
    if not os.path.isfile(CSV_FILE):
        print("CSV file missing. Cannot generate graph.")
        return

    try:
        df = pd.read_csv(CSV_FILE)
        if df.empty or len(df) < 1:
            print("CSV is empty. Skipping graph creation.")
            return

        # Ensure strings are parsed safely
        df['Date'] = df['Date'].astype(str)

        fig = px.line(
            df, 
            x='Date', 
            y='Leaderboard Position', 
            title=f"Geometry Dash Global Rank: {TARGET_USERNAME}",
            markers=True
        )

        fig.update_layout(
            yaxis=dict(autorange="reversed", title="Leaderboard Position (Lower is Better)"),
            xaxis=dict(type="category", title="Date"),
            template="plotly_dark"
        )

        fig.write_html(GRAPH_FILE)
        print("Successfully generated index.html!")
    except Exception as e:
        print(f"Error drawing graph layout: {e}")

if __name__ == "__main__":
    print("Starting tracker process...")
    current_rank = fetch_gd_rank(TARGET_USERNAME)
    if current_rank is not None:
        log_to_csv(current_rank)
        generate_graph()
    else:
        print("Failed to secure current rank. Process halted.")
