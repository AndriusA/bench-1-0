python3 ../../plots/make_plot.py --filter=totalBytes_Total --units=M mac-loading-rc2.csv mac-loading-traffic.png
python3 ../../plots/make_plot.py --filter=totalBytes_Total --units=M win-loading-rc2.csv win-loading-traffic.png

python3 ../../plots/make_plot.py --filter=pageLoadTime_Total --units=K mac-loading-rc2.csv mac-loading-pageLoad.png
python3 ../../plots/make_plot.py --filter=pageLoadTime_Total --units=K win-loading-rc2.csv win-loading-pageLoad.png

python3 ../../plots/make_plot.py --filter=TotalPrivateMemory --units=M mac-memory-rc2.csv mac-memory.png
python3 ../../plots/make_plot.py --filter=TotalPrivateMemory --units=M win-memory-rc2.csv win-memory.png
