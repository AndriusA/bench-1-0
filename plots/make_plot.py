import argparse
import re

import matplotlib
import matplotlib.pyplot as plt
import pandas

from typing import Dict, Optional, Tuple
from matplotlib.lines import Line2D

def get_extra_title(metric: str, units: str) -> Optional[str]:
  if metric == 'speedometer3' or metric == 'jetstream' or metric == 'motionmark':
    return 'higher is better'
  if metric.find('ytes') != -1 or metric.find('emory') != -1:
    return f'{units}B, lower is better'
  if metric.find('LoadTime') != -1:
    if units == 'K':
      return f's, lower is better'
  return None

def get_scale(units: str) -> float:
  if units == 'K':
    return 1000
  if units == 'M':
    return 1000 * 1000
  if units == 'G':
    return 1000 * 1000 * 1000
  return 1

def get_color(browser:str) -> str:
  if browser.find('Nightly') != -1:
    return 'fuchsia'
  if browser.find('Brave') != -1:
    return 'orangered'
  if browser.find('ChromeUBO') != -1:
    return 'peru'
  if browser.find('Chrome') != -1:
    return 'green'
  if browser.find('Opera') != -1:
    return 'red'
  if browser.find('Firefox') != -1:
    return 'salmon'
  if browser.find('Edge') != -1:
    return 'skyblue'
  if browser.find('Safari') != -1:
    return 'dodgerblue'
  if browser.find('DDG') != -1:
    return 'hotpink'
  return 'grey'

parser = argparse.ArgumentParser()
parser.add_argument('input_csv', type=str)
parser.add_argument('output_png', type=str)
parser.add_argument('--filter', type=str)
parser.add_argument('--units', choices=['K', 'M', 'G'])
parser.add_argument('--legend', action='store_true')
args = parser.parse_args()

matplotlib.use('Agg')
matplotlib.rcParams.update({'figure.autolayout': True})
matplotlib.rcParams.update({'figure.autolayout': True})
matplotlib.rcParams.update({'errorbar.capsize': 5})

# global parameters
width = 0.3   # width for barplot
barWidth = 0.3

# increase font
font = {'weight' : 'medium',
        'size'   : 14}
matplotlib.rc('font', **font)

cols = ['metric', 'browser', 'version', 'avg', 'stdev']
perf=pandas.read_csv(args.input_csv, usecols=cols, decimal=".", quotechar='"', index_col=False)
legend : Dict[Tuple[str, str], str] = {}
by_metric = perf[cols].groupby(['metric'], sort=True)

def should_skip(x):
  if args.filter is None:
    return False
  return re.search(args.filter, x.iat[0, 0]) is None

size = 0
for _, data in by_metric:
  if not should_skip(data):
    size += 1

scale = get_scale(args.units)

plt.figure(figsize=(10 * size, 8))
index = 0
for _, data in by_metric:
  if should_skip(data):
    continue
  metric = data.iat[0, 0]
  print(f'\n{metric}:')
  grouped = data.groupby(['browser'], sort=True)
  index += 1
  plt.subplot(1, size, index)
  extra_title = get_extra_title(metric, args.units)
  if extra_title:
    metric += f'\n({extra_title})'
  plt.title(metric)
  for name, group in grouped:
    assert group.shape[0] == 1
    browser = group.iat[0, 1]
    version = group.iat[0, 2]
    avg = group.iat[0, 3] / scale
    err = group.iat[0, 4] / scale
    print(browser, '{:.2f} ± {:.2f}'.format(avg, err))
    color = get_color(browser)
    legend[(browser, version)] = color
    plt.bar(x = '{}\n{:.2f}\n±{:.2f}'.format(browser, avg, err),
      height = avg,
      yerr = err,
      width=barWidth,
      color = color)

legend_lines = []
browser_list = []
print('\nBrowsers:')
for (browser, version), color in legend.items():
  browser_list.append(browser + ' ' + str(version))
  legend_lines.append(Line2D([0], [0], color = color, lw = 2))
  print(f'{browser} {version}')

plt.subplot(1, size, 1)
if args.legend:
  plt.legend(legend_lines, browser_list)

plt.savefig(args.output_png)
