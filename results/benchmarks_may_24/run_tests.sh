#!/bin/sh
python3 ../../measure.py benchmarks all scenarios/benchmarks.txt --debug --repeat=10 --retry-count=2
