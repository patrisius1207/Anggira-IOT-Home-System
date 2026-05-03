#!/usr/bin/env bash

# Load environment variables
if [ -f "$HOME/.anggira_env.sh" ]; then
    source "$HOME/.anggira_env.sh"
fi

BASE="$HOME/anggira"

ANGGIRA="$BASE/anggira.py"
DASH="$BASE/dashboard.py"
MUSIC="$BASE/stream_server.py"
BOT="$BASE/bot.py"

LOG="$HOME/system.log"

{
    echo "$(date) SYSTEM START"
    echo "$(date) START launcher"
} >> "$LOG"

start() {
    NAME=$1
    FILE=$2
    LOGFILE=$3

    while true; do
        # Check if process is already running
        if pgrep -f "$FILE" > /dev/null; then
            echo "$(date) $NAME already running, skip..." >> "$LOG"
            sleep 5
            continue
        fi

        echo "$(date) START $NAME" >> "$LOG"

        if [ -f "$FILE" ]; then
            python3 -u "$FILE" >> "$LOGFILE" 2>&1
        else
            echo "$(date) ERROR: $FILE not found" >> "$LOG"
            sleep 3
            continue
        fi

        EXIT_CODE=$?
        echo "$(date) $NAME EXIT code=$EXIT_CODE, restarting in 3s..." >> "$LOG"
        sleep 3
    done
}

start anggira "$ANGGIRA" "$HOME/anggira.log" &
start dashboard "$DASH" "$HOME/dashboard.log" &
start music "$MUSIC" "$HOME/stream_server.log" &
start bot "$BOT" "$HOME/bot.log" &

wait
