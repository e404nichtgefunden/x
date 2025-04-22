+++ run_bot.sh
+#!/bin/bash
+
+# Install required dependencies
+pip3 install python-telegram-bot --upgrade
+
+# Function to start the bot
+start_bot() {
+    echo "Starting Telegram bot..."
+    nohup python3 terminal1.py > bot_log.txt 2>&1 &
+    echo $! > bot.pid
+    echo "Bot started with PID $(cat bot.pid)"
+}
+
+# Function to check if bot is running
+check_bot() {
+    if [ -f bot.pid ]; then
+        PID=$(cat bot.pid)
+        if ps -p $PID > /dev/null; then
+            return 0  # Bot is running
+        else
+            return 1  # Bot is not running
+        fi
+    else
+        return 1  # PID file doesn't exist
+    fi
+}
+
+# Start the bot initially
+start_bot
+
+# Monitor and restart if needed
+while true; do
+    sleep 30  # Check every 30 seconds
+    
+    if ! check_bot; then
+        echo "Bot is not running. Restarting..."
+        start_bot
+    fi
+done
