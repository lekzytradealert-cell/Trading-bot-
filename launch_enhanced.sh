cd ~/lekzy_railway_bot

echo "🤖 Starting Enhanced Trading Bot..."
echo "📁 Directory: $(pwd)"
echo "⏰ Time: $(date)"
echo "🌍 Timezone: Europe/Paris (UTC+1)"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found!"
    exit 1
fi

# Check if enhanced bot exists
if [ ! -f "enhanced_bot.py" ]; then
    echo "❌ enhanced_bot.py not found!"
    exit 1
fi

# Set environment variable for Telegram token
export TELEGRAM_BOT_TOKEN="8411003379:AAEgw9b3eE943a0G5eMAC9zNKnAJPD6qGJ4"

echo "🚀 Launching Enhanced Bot..."
echo "📱 Bot Token: ${TELEGRAM_BOT_TOKEN:0:10}..."

# Start the enhanced bot
while true; do
    echo "🔄 Starting enhanced_bot.py..."
    python enhanced_bot.py
    
    EXIT_CODE=$?
    echo "⚠️ Bot exited with code $EXIT_CODE"
    echo "🔄 Restarting in 10 seconds..."
    sleep 10
done
