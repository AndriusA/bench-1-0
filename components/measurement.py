# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import List, Optional, Tuple, Type

from components.browser import Browser

class MeasurementState:
  urls: List[str]
  low_delays_for_testing = False


class Measurement:
  state: MeasurementState

  def __init__(self, state: MeasurementState):
    self.state = state

  def Run(
      self, iteration: int,
      browser_class: Type[Browser]) -> List[Tuple[str, Optional[str], float]]:
    raise RuntimeError('Not implemented')
