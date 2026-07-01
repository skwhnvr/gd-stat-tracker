import os
import csv
import requests
import matplotlib.pyplot as plt
from datetime import datetime

# --- CONFIGURATION ---
TARGET_USERNAME = "skyewhenever"  # <-- REPLACE WITH YOUR EXACT GD USERNAME
CSV_FILE = "gd_rank_history.csv"
GRAPH_FILE = "graph.png"
# ---------------------

def fetch_gd_rank(username):
    # Using GDBrowser's public API bypasses Cloudflare blocks automatically
    url = f"https://gdbrowser.com/api/profile/{username}"
    
    try:
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            print(f"GDBrowser API error: Status code {response.status_code}")
            return None
            
        data = response.json()
        
        # Extract rank safely
        rank = data.get("rank", 0)
        
        if rank == 0:
            print("Profile fetched, but no global rank found on this account.")
            return None
            
        return int(rank)

    except Exception as e:
        print(f"Network error trying to fetch player profile: {e}")
        return None

def log_to_csv(rank):
    file_exists = os.path.isfile(CSV_FILE)
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Leaderboard Position"])
        writer.writerow([date_str, rank])

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
                dates.append(row[0])
                ranks.append(int(row[1]))

    if not ranks:
        return

    plt.figure(figsize=(10, 5))
    plt.plot(dates, ranks, marker='o', color='#2da44e', linewidth=2, label="Leaderboard Rank")
    
    plt.title(f"Geometry Dash Global Rank: {TARGET_USERNAME}", fontsize=14, fontweight='bold')
    plt.xlabel("Date", fontsize=11)
    plt.ylabel("Leaderboard Position (Lower is Better)", fontsize=11)
    
    plt.gca().invert_yaxis()  # Keeps higher ranks visually higher on the chart
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(GRAPH_FILE, dpi=150)
    plt.close()

if __name__ == "__main__":
    current_rank = fetch_gd_rank(TARGET_USERNAME)
    if current_rank is not None:
        log_to_csv(current_rank)
        generate_graph()
        print(f"Successfully logged rank: {current_rank}")
