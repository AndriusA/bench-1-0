# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import re
import shutil
import subprocess
import time
import logging
import platform
import psutil

from tempfile import TemporaryDirectory
from typing import Dict, List, Optional, Type

from components.utils import is_mac, is_win


class Browser:
  binary_name: str
  use_user_data_dir: bool = True
  browsertime_binary: str
  args: List[str] = []

  temp_user_data_dir: Optional[TemporaryDirectory] = None
  process: Optional[subprocess.Popen] = None

  @classmethod
  def name(cls) -> str:
    return cls.__name__

  def profile_dir(self) -> str:
    raise RuntimeError('Not implemented')

  def get_version(self) -> Optional[str]:
    if is_win():
      output = subprocess.check_output(
        "wmic datafile where name=\"{:s}\" get version"
          .format(self.binary()
          .replace('\\','\\\\')),shell=True).decode('utf-8').rstrip()
      return output.split('\n')[1]
    if is_mac():
      output = subprocess.check_output([self.binary(), '--version']).decode('utf-8').rstrip()
      m = re.match(r'[a-zA-Z\ ]*([\d\.]+\d+)', output)
      if m is None:
        return None
      return m.group(1)

  def binary(self) -> str:
    if is_mac():
      return self.binary_mac()
    if is_win():
      return self.binary_win()
    raise RuntimeError('Unsupported platform')

  def binary_mac(self) -> str:
    return (f'/Applications/{self.binary_name}.app/Contents/MacOS/' +
            self.binary_name)

  def binary_win(self) -> str:
    raise RuntimeError('Not implemented')

  def extra_process(self) -> List[str]:
    return []

  def get_start_cmd(self, use_source_profile=False) -> List[str]:
    return [self.binary()] + self.get_args(use_source_profile)

  def get_args(self, use_source_profile=False) -> List[str]:
    args = []
    if self.use_user_data_dir:
      if use_source_profile:
        args.append(f'--user-data-dir={self._get_source_profile()}')
      else:
        args.append(f'--user-data-dir={self._get_target_profile()}')

    args.extend(self.args)
    return args

  def _get_source_profile(self) -> str:
    profile = os.path.join(os.curdir, 'browser_profiles', platform.system(),
                           self.name())
    return os.path.abspath(profile)

  def _get_target_profile(self) -> str:
    if self.use_user_data_dir:
      if self.temp_user_data_dir is None:
        self.temp_user_data_dir = TemporaryDirectory(prefix=self.name() +
                                                     '-user-data-')
      return self.temp_user_data_dir.name
    assert self.profile_dir()
    return self.profile_dir()

  def prepare_profile(self):
    if not self.use_user_data_dir:
      return

    target_profile = self._get_target_profile()
    if os.path.exists(target_profile):
      shutil.rmtree(target_profile)
    if not os.path.exists(self._get_source_profile()):
      raise RuntimeError('Can\'t find source profile')
    shutil.copytree(self._get_source_profile(), self._get_target_profile())

  def start(self, use_source_profile=False):
    assert self.process is None
    logging.debug(self.get_start_cmd(use_source_profile))
    self.process = subprocess.Popen(self.get_start_cmd(use_source_profile),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

  def terminate(self, timeout = 10):
    self.do_terminate(timeout)
    try:
      if self.temp_user_data_dir is not None:
        self.temp_user_data_dir.cleanup()
    except:
      pass

  def do_terminate(self, timeout):
    if self.process is None:
      return
    try:
      self.process.terminate()
    except:
      pass

    time_spend = 0
    while self.process.poll() is not None and time_spend < timeout:
      time.sleep(1)
      time_spend += 1

    if self.process.poll() is not None:
      logging.info('Killing %s pid %d', self.binary_name, self.process.pid)
      try:
        self.process.kill()
      finally:
        pass

  def open_url(self, url: str):
    if self.process is None:
      self.process = subprocess.Popen(self.get_start_cmd() + [url], stdout=subprocess.PIPE)
      return

    rv = subprocess.call(self.get_start_cmd() + [url], stdout=subprocess.PIPE)
    if self.name() != 'Opera':
      assert rv == 0


class _Chromium(Browser):
  browsertime_binary = 'chrome'


class Brave(_Chromium):
  binary_name = 'Brave Browser'

  def binary_win(self) -> str:
    return os.path.expandvars(
        R'%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe')

class BraveBeta(_Chromium):
  binary_name = 'Brave Browser Beta'

  def binary_win(self) -> str:
    return os.path.expandvars(
        R'%ProgramFiles%\BraveSoftware\Brave-Browser-Beta\Application\brave.exe')

class BraveNightly(_Chromium):
  binary_name = 'Brave Browser Nightly'

  def binary_win(self) -> str:
    return os.path.expandvars(
        R'%ProgramFiles%\BraveSoftware\Brave-Browser-Nightly\Application\brave.exe')


class DDG(Browser):
  binary_name = 'DuckDuckGo'
  use_user_data_dir = False

  def binary_win(self) -> str:
    return os.path.expandvars(
        R'%ProgramFiles%\WindowsApps\DuckDuckGo.DesktopBrowser_0.63.3.0_x64__ya2fgkz3nks94\WindowsBrowser\DuckDuckGo.exe')

  def profile_dir(self) -> str:
    if is_mac():
      return '~/Library/Containers/com.duckduckgo.macos.browser/Data/Library/Application Support/'
    raise RuntimeError('Not implemented')

  def get_version(self) -> Optional[str]:
    return None

  def extra_process(self) -> List[str]:
    return ['DuckDuckGo', 'com.apple.WebKit']

  def open_url(self, url: str):
    if is_mac():
      if self.process is None:
        self.process = subprocess.Popen(self.get_start_cmd() + [url], stdout=subprocess.PIPE)
        return
      rv = subprocess.check_call(['open', '-a', 'DuckDuckGo', url], stdout=subprocess.PIPE)
    else:
      super().open_url(url)


class Chrome(_Chromium):
  binary_name = 'Google Chrome'

  def binary_win(self) -> str:
    return os.path.expandvars(
        R'%ProgramFiles%\Google\Chrome\Application\chrome.exe')


class ChromeUBO(Chrome):
  pass


class Opera(_Chromium):
  binary_name = 'Opera'
  args = ['--ran-launcher']

  def binary_win(self) -> str:
    return os.path.expandvars(
        R'%USERPROFILE%\AppData\Local\Programs\Opera\opera.exe')

class Edge(Browser):
  binary_name = 'Microsoft Edge'
  browsertime_binary = 'edge'

  def binary_win(self) -> str:
    return os.path.expandvars(
        R'%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe')


class Safari(Browser):
  binary_name = 'Safari'
  use_user_data_dir = False
  browsertime_binary = 'safari'

  def profile_dir(self) -> str:
    if is_mac():
      return '~/Library/Safari'
    raise RuntimeError('Not implemented')

  def get_version(self) -> Optional[str]:
    args = ['/usr/libexec/PlistBuddy',
            '-c',
            'print :CFBundleShortVersionString',
            '/Applications/Safari.app/Contents/Info.plist']
    return subprocess.check_output(args).decode('utf-8').strip()


class Firefox(Browser):
  binary_name = 'Firefox'
  use_user_data_dir = False
  browsertime_binary = 'firefox'

  def profile_dir(self) -> str:
    if is_mac():
      return '~/Library/Application Support/Firefox/'
    if is_win():
      return os.path.expandvars(
          R'%USERPROFILE%\AppData\Roaming\Mozilla\Firefox')
    raise RuntimeError('Not implemented')

  def binary_win(self) -> str:
    return os.path.expandvars(R'%ProgramW6432%\Mozilla Firefox\firefox.exe')

  def do_terminate(self, timeout):
    if is_win():
      subprocess.call(['taskkill.exe', '/IM', 'firefox.exe'])
    else:
      super().do_terminate(timeout)

  def extra_process(self) -> List[str]:
    if is_win():
      return ['firefox', 'Firefox', 'plugin-container']
    return super().extra_process()


SUPPORTED_BROWSER_LIST: List[Type[Browser]] = [Brave, BraveBeta, BraveNightly, Chrome, ChromeUBO, Opera, Edge, Firefox, DDG]
DEFAULT_BROWSER_LIST: List[Type[Browser]] = [Brave, Chrome, ChromeUBO, Opera, Edge, Firefox]
if is_mac():
  SUPPORTED_BROWSER_LIST.append(Safari)
  DEFAULT_BROWSER_LIST.append(Safari)

BROWSER_LIST_MAP: Dict[str, Type[Browser]] = {}
for b in SUPPORTED_BROWSER_LIST:
  BROWSER_LIST_MAP[b.name()] = b

def get_browser_classes_from_str(name: str) -> List[Type[Browser]]:
  if name == 'default':
    return DEFAULT_BROWSER_LIST
  result: List[type[Browser]] = []
  for b in name.split(','):
    cls = BROWSER_LIST_MAP.get(b)
    if cls is None:
      raise RuntimeError(f'No browser with name {b} found')
    result.append(cls)

  return result
