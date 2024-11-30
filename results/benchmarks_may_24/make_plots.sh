#!/bin/sh
python3 ../../plots/make_plot.py win_bench_rc2.csv win_bench_rc2.png --filter="^motionmark$|^speedometer3$|^jetstream$" --legend
python3 ../../plots/make_plot.py mac_bench_rc2.csv mac_bench_rc2.png --filter="^motionmark$|^speedometer3$|^jetstream$" --legend
