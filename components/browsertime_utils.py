# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import os
import logging
import subprocess

from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from components.browser import Browser
from components.utils import is_win

DEFAULT_CHROME_OPTIONS = [
  '--new-window',
  '--no-default-browser-check',
  '--no-first-run',
  '--password-store=basic',
  '--use-mock-keychain',
  '--disable-features=CalculateNativeWinOcclusion',
  '--remote-debugging-port=9222']


def _get_total_transfer_bytes(har: Dict) -> int:
  total_bytes = 0
  for e in har['log']['entries']:
    res = e['response']
    if '_transferSize' in res:
      total_bytes += res['_transferSize']
    else:
      if 'bodySize' in res:
        try:
          total_bytes += res['bodySize']
        except:
          pass
      if 'headersSize' in res:
        try:
          total_bytes += res['headersSize']
        except:
          pass
  return total_bytes


def run_browsertime(browser: Browser, cmd: str, result_dir: str, wait_for_load: bool,
                    key: Optional[str], startup_delay: int,
                    extra_args: List[str]) -> List[Tuple[str, Optional[str], float]]:
  assert browser.browsertime_binary is not None

  npm_binary = 'npm.cmd' if is_win() else 'npm'
  args = ([npm_binary, 'exec', 'browsertime', '--'] +
          ['-b', browser.browsertime_binary] + ['-n', '1'] +
          ['--useSameDir', '--resultDir', f'{result_dir}'] +
          ['--browserRestartTries', '0'] +
          ['--viewPort', 'maximize'] +
          [f'--{browser.browsertime_binary}.binaryPath',
           browser.binary()])
  time_to_run = 0
  if not wait_for_load:
    time_to_run = 15 * 1000
    args.extend(['--pageCompleteCheck', 'return true'])
    args.extend(['--pageCompleteCheckStartWait', str(time_to_run)])
    args.extend(['--pageLoadStrategy', 'none'])

  args.extend(extra_args)
  args.extend(['--timeToSettle', str(startup_delay)])
  args.append('--chrome.noDefaultOptions')
  args.append('--firefox.noDefaultOptions')
  args.append('--firefox.disableBrowsertimeExtension')
  for arg in browser.get_args() + DEFAULT_CHROME_OPTIONS:
    assert arg.startswith('--')
    args.extend(['--chrome.args', arg[2:]])

  args.append(cmd)
  logging.debug(args)
  subprocess.check_call(args)
  output_file = os.path.join(result_dir, 'browsertime.json')
  with open(output_file, 'r', encoding='utf-8') as output:
    output_json = json.load(output)

  results: List[Tuple[str, Optional[str], float]] = []

  har_json = None
  try:
    har_file = os.path.join(result_dir, 'browsertime.har')
    with open(har_file, 'r', encoding='utf-8') as har:
      har_json = json.load(har)
  except FileNotFoundError:
    pass

  for item in output_json:
    url = item['info']['url']
    current_key = key if key is not None else urlparse(url).netloc
    timings = item['statistics']['timings']
    firstPaint = timings['firstPaint']['mean'] if 'firstPaint' in timings else -1
    results.append(('firstPaint', current_key, firstPaint))

    largestContentfulPaint = (
      timings['largestContentfulPaint']['renderTime']['mean']
      if 'largestContentfulPaint' in timings else -1
    )
    results.append(('largestContentfulPaint', current_key,
                    largestContentfulPaint))

    pageTimings = timings.get('pageTimings')

    dcl = (
      pageTimings['domContentLoadedTime']['mean']
      if pageTimings is not None and 'domContentLoadedTime' in pageTimings
      else -1
    )

    if dcl == 0:
      dcl = time_to_run
    results.append(('domContentLoadedTime', current_key, dcl))

    pageLoadTime = (
      pageTimings['pageLoadTime']['mean']
      if pageTimings is not None and 'pageLoadTime' in pageTimings else -1
    )
    if pageLoadTime == 0:
      pageLoadTime = time_to_run
    results.append(('pageLoadTime', current_key, pageLoadTime))

    for extra in item['extras']:
      for metric, value in extra.items():
        if isinstance(value, list):
          for v in value:
            results.append((metric, key, v))
        else:
          results.append((metric, key, float(value)))
  if har_json:
    results.append(('totalBytes', key, _get_total_transfer_bytes(har_json)))
  return results
