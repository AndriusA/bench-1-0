#!/usr/bin/env python3
import argparse
import logging
from typing import List

from components.browser import Browser, get_browser_classes_from_str

def make_profile():
  log_format = '%(asctime)s: %(message)s'
  logging.basicConfig(level=logging.DEBUG, format=log_format)

  parser = argparse.ArgumentParser()
  parser.add_argument('browser', type=str)
  args = parser.parse_args()
  browser_classes = get_browser_classes_from_str(args.browser)
  browsers: List[Browser] = []
  for browser_class in browser_classes:
    browser: Browser = browser_class()
    browser.start(use_source_profile=True)
    browsers.append(browser)

  print("Press any key to close browsers...")
  input()
  for browser in browsers:
    browser.terminate()

make_profile()
