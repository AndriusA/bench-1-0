import argparse
from typing import Set
import psutil

from components.browser import Firefox, Safari
from components.memory_metrics import get_all_children, get_memory_metrics, get_memory_metrics_for_processes

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('browser', type=str)
  parser.add_argument('user_data_dir', type=str, nargs='?')
  args = parser.parse_args()
  matched_processes: Set[psutil.Process] = set()
  if args.browser == 'firefox':
    metrics = get_memory_metrics(Firefox())
  elif args.browser == 'safari':
    metrics = get_memory_metrics(Safari())
  else:
    for p in psutil.process_iter():
      try:
        if args.user_data_dir is not None:
          if p.cmdline().count(f'--{args.user_data_dir}'):
            if not p in matched_processes:
              matched_processes.add(p)
              matched_processes.update(get_all_children(p.pid))
        elif args.browser == 'firefox':
          if p.cmdline()[0].find('irefox') != -1:
            if not p in matched_processes:
              matched_processes.add(p)
              matched_processes.update(get_all_children(p.pid))
        elif args.browser == 'safari':
          if p.name().find('Safari') != -1 or p.name().find('com.apple.WebKit') != -1:
            if not p in matched_processes:
              matched_processes.add(p)
              matched_processes.update(get_all_children(p.pid))
      except:
        pass
    metrics = get_memory_metrics_for_processes(matched_processes)

  print('{')
  #TODO: rewrite
  index = 0
  for (m,v) in metrics:
    print(f'"{m}":{v}')
    index += 1
    if index < len(metrics):
      print(',')
  print('}')

if __name__ == '__main__':
    main()
