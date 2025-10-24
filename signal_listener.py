import json, time, requests

def run_signal_listener():
    with open("config.json") as f:
        config = json.load(f)

    while True:
        print("📡 Listening for Pocket Option & TradingView signals...")
        try:
            # Fetch Pocket Option signals
            pocket_resp = requests.get(config["sources"]["pocket_option"]["url"])
            pocket_data = pocket_resp.json()

            # Fetch TradingView webhook data (mock test)
            tv_resp = requests.get(config["sources"]["tradingview"]["webhook_url"])
            tv_data = tv_resp.json()

            print("✅ Pocket Option Signal:", pocket_data)
            print("📈 TradingView Signal:", tv_data)

        except Exception as e:
            print("❌ Error fetching signals:", e)

        time.sleep(config["refresh_interval"])  # Wait before next fetch

if __name__ == "__main__":
    run_signal_listener()
