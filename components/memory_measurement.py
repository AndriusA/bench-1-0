# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
import time

from typing import List, Optional, Tuple, Type

from components.browser import Browser
from components.measurement import Measurement, MeasurementState
from components.memory_metrics import get_memory_metrics


class MemoryMeasurement(Measurement):
  start_delay = 5
  open_url_delay = 15
  measure_delay = 45
  terminate_delay = 5

  def __init__(self, state: MeasurementState) -> None:
    super().__init__(state)
    if state.low_delays_for_testing:
      self.start_delay = 1
      self.open_url_delay = 1
      self.measure_delay = 5
      self.terminate_delay = 5

  def Run(
      self, _,
      browser_class: Type[Browser]) -> List[Tuple[str, Optional[str], float]]:
    browser = browser_class()
    metrics = []
    try:
      browser.prepare_profile()
      browser.start()
      time.sleep(self.start_delay)
      for url in self.state.urls:
        if url.startswith('#') or url.startswith('/'):
          continue
        if url == '':
          break
        browser.open_url(url)
        time.sleep(self.open_url_delay)

      time.sleep(self.measure_delay)

      assert browser.process is not None
      for metric, value in get_memory_metrics(browser):
        metrics.append((metric, None, value))
      browser.terminate()
    except:
      browser.terminate()
      raise

    time.sleep(self.terminate_delay)
    return metrics
