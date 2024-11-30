#!/usr/bin/env python3
# Copyright (c) 2024 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
from components.result_map import ResultMap
def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('csv_file', type=str)
  parser.add_argument('browser', type=str)
  parser.add_argument('browser_version', type=str)
  parser.add_argument('metric', type=str)
  parser.add_argument('value_list', type=str)
  parser.add_argument('--key', type=str)
  args = parser.parse_args()

  values = args.value_list.split(',')
  results = ResultMap()
  for v in values:
    value = float(v)
    results.addValue(args.browser, args.browser_version, args.metric, args.key, value)

  results.write_csv(args.csv_file, True)

main()
