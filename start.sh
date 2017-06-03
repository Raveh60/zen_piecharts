#!/bin/sh

nohup python3 zen_piechart.py > chart.log 2>&1 &
echo $! > chart_pid.txt
