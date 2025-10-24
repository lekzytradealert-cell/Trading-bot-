#!/data/data/com.termux/files/usr/bin/bash
# --- Auto-restart + Telegram alert + Logging ---

# Telegram credentials
TELEGRAM_TOKEN="8358721170:AAGOG7151_fNYEtiNXaXCrd3r01bx3nkCDY"
CHAT_ID="6307001401"

# Log directory
LOG_DIR="$HOME/trading_bot/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/bot.log"

# Function to send Telegram alert
send_alert() {
    MESSAGE="$1"
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$TIMESTAMP] $MESSAGE" >> "$LOG_FILE"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d chat_id="${CHAT_ID}" \
        -d text="${MESSAGE}" > /dev/null
}

# Start message
send_alert "⚙️ RSI Bot auto-started successfully!"

# Continuous restart loop
while true
do
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$TIMESTAMP] ▶️ Starting bot..." >> "$LOG_FILE"
    
    python3 ~/trading_bot/light_bot.py >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?
    
    send_alert "⚠️ Bot stopped (exit code: ${EXIT_CODE}). Restarting in 10 seconds..."
    sleep 10
done
