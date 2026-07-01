import os
import csv
import requests
import matplotlib.pyplot as plt
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

    dates = []
    ranks = []
    
    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader) 
        for row in reader:
            if row:
                # Convert date strings to actual datetime objects for accurate spacing
                dates.append(datetime.strptime(row[0], "%Y-%m-%d"))
                ranks.append(int(row[1]))

    if not ranks:
        return

    plt.figure(figsize=(10, 5))
    
    # Using plot_date to keep spacing mathematically accurate across calendar days
    plt.plot_date(dates, ranks, linestyle='-', marker='o', color='#2da44e', linewidth=2)
    
    plt.title(f"Geometry Dash Global Rank: {TARGET_USERNAME}", fontsize=14, fontweight='bold')
    plt.xlabel("Date", fontsize=11)
    plt.ylabel("Leaderboard Position (Lower is Better)", fontsize=11)
    
    plt.gca().invert_yaxis()  
    
    plt.gcf().autofmt_xdate() # Automatically tilts and formats dates nicely
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    plt.savefig(GRAPH_FILE, dpi=150)
    plt.close()

if __name__ == "__main__":
    current_rank = fetch_gd_rank(TARGET_USERNAME)
    if current_rank is not None:
        log_to_csv(current_rank)
        generate_graph()
        print(f"Successfully logged rank: {current_rank}")
