import ctypes
import sys

def focus_console_window():
  # TODO: Support other operating systems
  if sys.platform == "win32":
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
      ctypes.windll.user32.ShowWindow(hwnd, 9)
      ctypes.windll.user32.SetForegroundWindow(hwnd)
