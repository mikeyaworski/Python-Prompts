import ctypes
import sys
import os

def is_windows():
  return os.name == 'nt'

def is_mac():
  return sys.platform == 'darwin'

def focus_console_window():
  # TODO: Support other operating systems
  if is_windows():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
      ctypes.windll.user32.ShowWindow(hwnd, 9)
      ctypes.windll.user32.SetForegroundWindow(hwnd)
