import os
import csv
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
# Import zoneinfo to strictly handle the UK timezone
from zoneinfo import ZoneInfo 

# --- CONFIGURATION ---
TARGET_USERNAME = "skyewhenever"
CSV_FILE = "gd_rank_history.csv"
GRAPH_FILE = "graph.png"
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
    # 🌟 THE FIX: Force the script to fetch the time specifically for Europe/London
    uk_tz = ZoneInfo("Europe/London")
    date_str = datetime.now(uk_tz).strftime("%Y-%m-%d")
    
    rows = []
    updated = False

    # Read existing data to prevent duplicate date rows if run multiple times a day
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

def generate_graph():
    if not os.path.isfile(CSV_FILE):
        return

    # Read the data using pandas for easier charting
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return

    # Convert Date column to actual datetime objects
    df['Date'] = pd.to_datetime(df['Date'])

    # Create an interactive line chart
    fig = px.line(
        df, 
        x='Date', 
        y='Leaderboard Position', 
        title=f"Geometry Dash Global Rank: {TARGET_USERNAME}",
        markers=True
    )

    # Style tweaks: Invert Y-axis (lower number = better rank) and add time filters
    fig.update_layout(
        yaxis=dict(autorange="reversed"), # Inverts the rank axis natively!
        template="plotly_dark",           # Clean dark mode look
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=30, label="1m", step="day", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            ),
            type="date"
        )
    )

    # Save as an interactive HTML webpage instead of a flat picture
    fig.write_html("index.html")
