# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import List, Optional, Tuple, Type
from urllib.parse import urlparse

from components.browsertime_utils import run_browsertime
from components.browser import Browser
from components.measurement import Measurement


class LoadingMeasurement(Measurement):
  def Run(
      self, iteration: int,
      browser_class: Type[Browser]) -> List[Tuple[str, Optional[str], float]]:
    urls = self.state.urls
    results: List[Tuple[str, Optional[str], float]] = []

    for index, url in enumerate(urls):
      if url.startswith('#') or url.startswith('/'):
        continue
      if url == '':
        break

      browser = browser_class()
      if browser.browsertime_binary is None:
        continue
      browser.prepare_profile()
      domain = urlparse(url).netloc
      result_dir = f'browsertime/{browser.name()}/{index}_{domain}/{iteration}/'
      res = run_browsertime(
          browser, url, result_dir, False, domain,
          1000 if self.state.low_delays_for_testing else 10000,
          [])

      results.extend(res)

    return results
