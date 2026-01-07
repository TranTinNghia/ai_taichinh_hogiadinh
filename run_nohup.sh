#!/bin/bash
nohup ./run.sh > logs/app.log 2>&1 &
echo "App đã khởi động với PID: $!"
echo "Logs được lưu tại: logs/app.log"
echo "Để dừng app, chạy: pkill -f 'python3 app.py' và pkill -f 'react-scripts'"
