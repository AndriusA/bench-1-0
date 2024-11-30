#!/usr/bin/env python3
# Copyright (c) 2024 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import logging
import os
import time
from typing import Dict, List

from components.browser import get_browser_classes_from_str
from components.measurement import MeasurementState
from components.result_map import ResultMap
from components.script_measurement import ScriptMeasurement
from components.loading_measurement import LoadingMeasurement
from components.memory_measurement import MemoryMeasurement


def get_measure_by_args(args):
  state = MeasurementState()
  state.low_delays_for_testing = args.low_delays_for_testing
  state.urls = args.urls_file.read().splitlines()

  if args.measure == 'memory':
    return MemoryMeasurement(state)
  if args.measure == 'loading':
    return LoadingMeasurement(state)
  if args.measure == 'script':
    return ScriptMeasurement(state)
  raise RuntimeError(f'No measurement {args.measure} found')

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('measure', type=str, choices=['memory', 'loading', 'script'])
  parser.add_argument('browser', type=str)
  parser.add_argument('urls_file',
                      type=argparse.FileType('r', encoding='utf-8'),
                      help='File with urls to test')
  parser.add_argument('--connectivity_profile', type=str)
  parser.add_argument('--verbose', action='store_true')
  parser.add_argument('--repeat', type=int, default=1)
  parser.add_argument('--low-delays-for-testing', action='store_true')
  parser.add_argument('--output', type=str, default='results.csv')
  parser.add_argument('--append', action='store_true')
  parser.add_argument('--retry-count', type=int, default=2)
  parser.add_argument('-d', '--debug', action='store_true')

  args = parser.parse_args()
  if args.debug:
    args.low_delays_for_testing = True
    args.verbose = True

  log_level = logging.DEBUG if args.verbose else logging.INFO
  log_format = '%(asctime)s: %(message)s'
  logging.basicConfig(level=log_level, format=log_format)

  header = None
  if args.append and os.path.isfile(args.output):
    with open(args.output, 'r', newline='', encoding='utf-8') as result_file:
      header = result_file.read()

  measure = get_measure_by_args(args)
  test_name: str = args.urls_file.name
  repeat: int = args.repeat

  browser_classes = get_browser_classes_from_str(args.browser)
  results = ResultMap()
  final_messages: List[str] = []

  versions: Dict[str, str] = {}

  for browser_class in browser_classes:
      browser = browser_class()
      version = browser.get_version()
      if version is None:
        version = "unknown"
      versions[browser.name()] = version

  run_index = 0
  total_runs = len(browser_classes) * args.repeat
  global_start_time = time.time()

  for index in range(args.repeat):
    for browser_class in browser_classes:
      browser_name = browser_class().name()
      version = versions[browser_name]
      logging.info('Testing %d/%s-%s', index, browser_name, version)
      attempt = 0
      run_index += 1
      while True:
        try:
          metrics = measure.Run(index, browser_class)
          logging.debug([test_name, browser_name, version, metrics])
          for metric, key, value in metrics:
            results.addValue(browser_name, version, metric, key, value)
          break
        except Exception as e:
          attempt += 1
          if args.retry_count is not None and attempt <= args.retry_count:
            logging.error('Got error %s, retrying', e)
            final_messages.append(
              f'{test_name}/{browser_name}/{index} failed')
          else:
            raise
      results.write_csv(header, args.output)
      total_spent = time.time() - global_start_time
      logging.info('### %d / %d spent %.1f min, remaining %.1f min',
                   run_index, total_runs,
                   total_spent / 60,
                   total_spent * (total_runs - run_index)/ run_index / 60)


  for msg in final_messages:
    logging.error(msg)


main()
