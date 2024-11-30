#!/bin/sh
python3 ../../add_results.py mac_bench_rc2.csv DDG 1.88.0 speedometer3 24.77,24.8,25.0,24.8,24.5
python3 ../../add_results.py mac_bench_rc2.csv DDG 1.88.0 motionmark 5790.96,5758.77,5492.82,5753.52,5834.86
python3 ../../add_results.py mac_bench_rc2.csv DDG 1.88.0 jetstream 321.553,311.066,312.063,318.794,309.751

python3 ../../add_results.py win_bench_rc2.csv DDG 0.81.1 speedometer3 4.69,4.81,4.38,4.86,4.71
python3 ../../add_results.py win_bench_rc2.csv DDG 0.81.1 motionmark 227.49,246.86,246.24,252.54,242.96
python3 ../../add_results.py win_bench_rc2.csv DDG 0.81.1 jetstream 91.368,91.824,92.841,91.812,90.096

python3 ../../add_results.py win_bench_rc2.csv Firefox 126.0.0.8895 speedometer3 4.60,4.59,4.79,4.29,4.69
python3 ../../add_results.py win_bench_rc2.csv Firefox 126.0.0.8895 jetstream 59.762,61.787,59.262,60.377,59.215
