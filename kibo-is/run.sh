#!/bin/bash
# run.sh - Manage KIBO.IS FastAPI backend process

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$DIR/uvicorn.pid"
LOG_FILE="$DIR/uvicorn.log"
PYTHON_BIN="/Users/iceman/Documents/Code/Kibo/.venv/bin/python"

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "KIBO.IS is already running with PID $(cat $PID_FILE)"
        return 1
    fi
    echo "Starting KIBO.IS FastAPI backend..."
    cd "$DIR"
    nohup "$PYTHON_BIN" -m uvicorn agent_gateway:app --host 0.0.0.0 --port 8000 > "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    sleep 2
    if kill -0 $PID 2>/dev/null; then
        echo "KIBO.IS started successfully with PID $PID"
    else
        echo "Failed to start KIBO.IS. Check log at $LOG_FILE"
    fi
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        echo "Stopping KIBO.IS PID $PID..."
        kill $PID
        rm -f "$PID_FILE"
        echo "Stopped."
    else
        echo "PID file not found. KIBO.IS might not be running."
    fi
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "KIBO.IS is RUNNING (PID $(cat $PID_FILE))"
        tail -n 10 "$LOG_FILE"
    else
        echo "KIBO.IS is STOPPED"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    restart)
        stop
        sleep 1
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac
