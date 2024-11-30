#!/usr/bin/env python3
# Copyright (c) 2024 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import csv
import statistics

from typing import Dict, List, Optional, Set, Tuple

class ResultMap():
  #  Dict[Tuple[metric, key, browser_spec], metric_values]
  _map: Dict[Tuple[str, Optional[str], str, str], List[float]] = {}
  _error: Dict[Tuple[str, Optional[str], str, str], float] = {}

  def addValue(self, browser: str, version: str, metric: str, key: Optional[str],
               value: float):
    s = metric.split('#error')
    if len(s) > 1:
      original_metric = s[0]
      index = (original_metric, key, browser, version)
      assert self._error.get(index) is None
      self._error[index] = value
    else:
      index = (metric, key, browser, version)
      self._map.setdefault(index, [])
      self._map[(metric, key, browser, version)].append(value)

  # Calculate *_Total metrics
  def calc_total_metrics(self):
    all_keys: Set[str] = set()
    total_metrics: Set[Tuple[str, str,str]] = set()
    for (metric, key, browser, version), _ in list(self._map.items()):
      if metric.endswith('_Total'):
        # Clear the old entries
        del self._map[(metric, key, browser, version)]
      else:
        if key is not None:
          all_keys.add(key)
          total_metrics.add((metric, browser, version))

    for (metric, browser, version) in total_metrics:
      total_metric_name = f'{metric}_Total'
      total_index = (total_metric_name, None, browser, version)
      self._map.setdefault(total_index, [])
      total = self._map[total_index]
      for key in all_keys:
        current = self._map.get((metric, key, browser, version))
        if current is None:
          continue
        for i in range(len(current)):
          if i >= len(total):
            total.append(0)
          total[i] += current[i]

  def write_csv(self, header: Optional[str], output_file: str):
    self.calc_total_metrics()
    with open(output_file, 'w', newline='', encoding='utf-8') as result_file:
      result_writer = csv.writer(result_file,
                                 delimiter=',',
                                 quotechar='"',
                                 quoting=csv.QUOTE_NONNUMERIC)
      if header is None:
        result_writer.writerow(['metric', 'browser', 'version'] +
                              ['avg', 'stdev', 'stdev%', '', 'raw_values..'])
      else:
        result_file.write(header)
      for (metric, key, browser, version), values in self._map.items():
        metric_str = metric + '_' + key if key is not None else metric
        error = self._error.get((metric, key, browser, version))
        avg = statistics.fmean(values)
        if error is None:
          stdev = statistics.stdev(values) if len(values) > 1 else 0
        else:
          stdev = error
        rstdev = stdev / avg if avg > 0 else 0
        result_writer.writerow([metric_str, browser, version] +
                                [avg, stdev, rstdev] + [''] + values)
