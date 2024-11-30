# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import os

from typing import List, Optional, Tuple, Type

from components.browsertime_utils import run_browsertime
from components.browser import Browser
from components.measurement import Measurement


class ScriptMeasurement(Measurement):
  def Run(
      self, iteration: int,
      browser_class: Type[Browser]) -> List[Tuple[str, Optional[str], float]]:
    urls = self.state.urls
    results: List[Tuple[str, Optional[str], float]] = []

    for index, name in enumerate(urls):
      browser = browser_class()
      if browser.browsertime_binary is None:
        continue
      script = os.path.join('benchmark_scripts', name)
      assert os.path.exists(script)
      browser.prepare_profile()
      result_dir = f'browsertime/{browser.name()}/{index}_{name}/{iteration}/'

      res = run_browsertime(
        browser, script, result_dir, False, None,
        1000 if self.state.low_delays_for_testing else 10000,
        ['--timeouts.script', str(30 * 60 * 1000)]
      )


      results.extend(res)

    return results
