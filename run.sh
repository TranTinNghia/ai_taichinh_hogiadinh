#!/bin/bash

BACKEND_PID=""
FRONTEND_PID=""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p logs

cleanup() {
    echo ""
    echo "Đang dừng các service..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        wait $BACKEND_PID 2>/dev/null
        echo "Backend đã dừng"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        wait $FRONTEND_PID 2>/dev/null
        echo "Frontend đã dừng"
    fi
    pkill -f "react-scripts" 2>/dev/null
    pkill -f "node.*react-scripts" 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

if ! command -v python3 &> /dev/null; then
    echo "Lỗi: python3 chưa được cài đặt"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "Lỗi: npm chưa được cài đặt"
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "Đang cài đặt dependencies cho frontend..."
    cd frontend
    npm install
    cd ..
fi

echo "Đang khởi động Backend..."
python3 app.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend đã khởi động (PID: $BACKEND_PID)"

sleep 3

echo "Đang khởi động Frontend..."
cd frontend
npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "Frontend đã khởi động (PID: $FRONTEND_PID)"

echo ""
echo "=========================================="
echo "Ứng dụng đã khởi động thành công!"
echo "Backend: http://100.91.247.70:5000"
echo "Frontend: http://100.91.247.70:3000"
echo "=========================================="
echo ""
echo "Logs được lưu tại:"
echo "  - Backend: logs/backend.log"
echo "  - Frontend: logs/frontend.log"
echo ""
echo "Nhấn Ctrl+C để dừng tất cả services"
echo ""

wait
