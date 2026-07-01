import os
import csv
import requests
import matplotlib.pyplot as plt
from datetime import datetime

# --- CONFIGURATION ---
ACCOUNT_ID = "18534734"  # <-- REPLACE WITH YOUR GEOMETRY DASH ACCOUNT ID
CSV_FILE = "gd_rank_history.csv"
GRAPH_FILE = "graph.png"
URL = "http://www.bombergames.com/database/getGJUserInfo20.php"
# ---------------------

def fetch_gd_rank(account_id):
    payload = {"secret": "Wmfd2893gb7", "targetAccountID": account_id}
    headers = {"User-Agent": ""}
    try:
        response = requests.post(URL, data=payload, headers=headers, timeout=10)
        if response.text == "-1" or not response.text:
            return None
        data_parts = response.text.split(":")
        for i in range(0, len(data_parts) - 1, 2):
            if data_parts[i] == "6":
                return int(data_parts[i+1]) if data_parts[i+1].isdigit() else 0
        return 0
    except Exception as e:
        print(f"Error fetching: {e}")
        return None

def log_to_csv(rank):
    file_exists = os.path.isfile(CSV_FILE)
    date_str = datetime.now().strftime("%Y-%m-%d") # Format as Year-Month-Day
    
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
        next(reader) # Skip header row
        for row in reader:
            if row:
                dates.append(row[0])
                ranks.append(int(row[1]))

    if not ranks:
        return

    # Style and plot the chart
    plt.figure(figsize=(10, 5))
    plt.plot(dates, ranks, marker='o', color='#2da44e', linewidth=2, label="Leaderboard Rank")
    
    # Custom tweaks for leaderboard tracking
    plt.title("Geometry Dash Global Rank Over Time", fontsize=14, fontweight='bold')
    plt.xlabel("Date", fontsize=11)
    plt.ylabel("Leaderboard Position (Lower is Better)", fontsize=11)
    
    # Invert the Y-axis so "Rank 100" is visually higher up than "Rank 5000"
    plt.gca().invert_yaxis() 
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the chart as an image file
    plt.savefig(GRAPH_FILE, dpi=150)
    plt.close()

if __name__ == "__main__":
    current_rank = fetch_gd_rank(ACCOUNT_ID)
    if current_rank is not None and current_rank > 0:
        log_to_csv(current_rank)
        generate_graph()
        print("Data logged and graph image regenerated successfully.")