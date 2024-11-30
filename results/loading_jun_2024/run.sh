python3 measure.py script Chrome,ChromeUBO,Brave,Opera,Edge scenarios/memory.txt --verbose --repeat=10 --output new-set-memory-9.csv
python3 measure.py memory DDG scenarios/new-set.txt --verbose --repeat=10 --output new-set-memory-9.csv --append
python3 measure.py memory Safari scenarios/new-set.txt --verbose --repeat=10 --output new-set-memory-9.csv --append
python3 measure.py memory Firefox scenarios/new-set.txt --verbose --repeat=10 --output new-set-memory-9.csv --append

python3 measure.py loading Chrome,ChromeUBO,Brave,Opera,Edge,Firefox scenarios/new-set.txt --verbose --repeat=10 --output new-set-loading-9.csv
python3 measure.py loading Safari scenarios/new-set.txt --verbose --repeat=10 --output new-set-loading-9.csv --append

#python3 measure.py script Brave scenarios/memory.txt --verbose --repeat=10 --output new-set-memory-5.csv
