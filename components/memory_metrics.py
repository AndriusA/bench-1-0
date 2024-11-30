import subprocess
import logging
import re
import math
import platform
import psutil
import asyncio

from typing import Dict, List, Optional, Set, Tuple, Type

from components.browser import Browser

async def _get_private_memory_usage_mac(name: str, pid: int) -> Optional[float]:
  process = await asyncio.subprocess.create_subprocess_exec(
      'vmmap', '--summary', str(pid),
      stderr=asyncio.subprocess.PIPE,
      stdout=asyncio.subprocess.PIPE)
  stdout, _ = await process.communicate()

  # https://docs.google.com/document/d/1vltgFPqylHqpxkyyCM9taVPWNOTJkzu_GjuqdEwYofM
  m = re.search('Physical footprint: *([\\d|.]*)(.)', stdout.decode())
  if m is None:
    return None

  val = float(m.group(1))

  assert len(m.group(2)) == 1
  scale = m.group(2)[0]

  ex = ['K', 'M', 'G'].index(scale) + 1
  mem = val * math.pow(1024, ex)
  logging.debug('Process %s (pid %d): %f %s %d %f', name, pid, val, scale, ex, mem)
  return mem


async def _get_private_memory_usage_win(name: str, pid: int) -> Optional[float]:
  p = await asyncio.subprocess.create_subprocess_exec(
      'powershell.exe', '-Command',
      ('WmiObject -class Win32_PerfFormattedData_PerfProc_Process' +
       f' -filter "IDProcess like {pid}" | ' +
       'Select-Object -expand PrivateBytes'),
       stdout = asyncio.subprocess.PIPE)
  stdout, _ = await p.communicate()
  if p.returncode != 0:
    return None
  try:
    pmf = float(stdout.decode().rstrip())
    logging.debug('process %s (pid %d) usage %f', name, pid, pmf)
    assert pmf > 0
    return pmf
  except:
    return None


async def _get_private_memory_usage(name: str, pid: int) -> Optional[float]:
  if platform.system() == 'Darwin':
    return await _get_private_memory_usage_mac(name, pid)
  if platform.system() == 'Windows':
    return await _get_private_memory_usage_win(name, pid)
  raise RuntimeError('Platform is not supported')

def get_all_children(pid: int) -> Set[psutil.Process]:
  process = psutil.Process(pid)
  child_processes = set()
  child_processes.add(process)
  for c in process.children(recursive=True):
    if c.is_running() and c.status() != psutil.STATUS_ZOMBIE:
      child_processes.add(c)
  return child_processes

def _find_main_process(processes: Set[psutil.Process]) -> Optional[psutil.Process]:
  pids: Set[int] = set()
  for p in processes:
    pids.add(p.pid)
  candidates = []
  for p in processes:
    try:
      if p.parent().pid in pids:
        continue
      if any(arg.startswith('--type=') for arg in p.cmdline()):
        continue

      candidates.append(p)
    except:
      pass

  if len(candidates) == 1:
    return candidates[0]
  return None

def get_memory_metrics_for_processes(processes: Set[psutil.Process]) -> List[Tuple[str, float]]:
  main_private: Optional[float] = None
  main_rss: Optional[float] = None
  gpu_private: float = 0.0
  total_private: float = 0.0

  tasks = []
  private_bytes: Dict[int, float] = {}
  loop = asyncio.get_event_loop()

  async def calc_private_bytes(name: str, pid: int):
    result = await _get_private_memory_usage(name, pid)
    if result is not None:
      private_bytes[pid] = result

  for p in processes:
    tasks.append(loop.create_task(calc_private_bytes(p.name(), p.pid)))
  if len(tasks) > 0:
    loop.run_until_complete(asyncio.wait(tasks))
  logging.debug('Async memory measurements are done')

  main_process = _find_main_process(processes)
  if main_process is not None:
    main_private = private_bytes[main_process.pid]
    main_rss = main_process.memory_info().rss

  for p in processes:
    try:
      private = private_bytes[p.pid]
      if private is None:
        # TODO: add warn?
        continue
      total_private += private
      if p.cmdline().count('--type=gpu-process') > 0:
        gpu_private += private
    except:
      pass

  metrics: List[Tuple[str, float]] = [('TotalPrivateMemory',  total_private)]
  if gpu_private > 0:
    metrics.append(('GpuProcessPrivate', gpu_private))
    if main_private is not None:
      non_gpu_child_private = total_private - gpu_private - main_private
      metrics.append(('NonGpuChildPrivate', non_gpu_child_private))

  if main_private is not None:
    metrics.append(('MainProcessPrivateMemory', main_private))

  return metrics


def get_memory_metrics(browser: Browser) -> List[Tuple[str, float]]:
  processes: Set[psutil.Process] = set()
  if browser.process is not None:
    try:
      processes = get_all_children(browser.process.pid)
    except:
      pass

  for p in browser.find_extra_processes():
    processes.add(p)
  return get_memory_metrics_for_processes(processes)
