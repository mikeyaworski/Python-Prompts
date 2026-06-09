import time
from InquirerPy import inquirer
from tkinter import filedialog, Tk
from typing import (
  Sequence,
  Callable,
  Any
)
from enum import Enum
from . import keybinds
from . import utils

# The toolkit used in InquirerPy breaks ANSI formatting, so we need to patch it.
from colorama import just_fix_windows_console
just_fix_windows_console()

Choice = str | tuple[str, str]
DefaultChoice = str | list[str]

def transform_choice(choice: Choice, default: DefaultChoice | None = None):
  if isinstance(choice, str):
    is_default = (isinstance(default, list) and choice in default) or (default and choice == default)
    return {
      'name': choice,
      'value': choice,
      'enabled': is_default,
    }
  elif isinstance(choice, tuple) and len(choice) == 2:
    display_name = choice[0]
    value = choice[1]
    is_default = (isinstance(default, list) and value in default) or (default and value == default)
    return {
      'name': display_name,
      'value': value,
      'enabled': is_default,
    }
  return choice

def get_multi_selections(message: str, choices: Sequence[Choice], default: DefaultChoice | None = None, required: bool = False):
  transformed_choices = [transform_choice(c, default) for c in choices]
  prompt = inquirer.fuzzy(
    message=message,
    choices=transformed_choices,
    mandatory=required,
    multiselect=True,
    cycle=False,
    prompt='Search:',
    qmark='',
    amark='',
    pointer='> ',
    marker='[X] ',
    marker_pl='[ ] ',
    exact_symbol=' [Exact]',
    vi_mode=False,
    keybindings={
      # Change the answer key from Enter to something random
      # so that we can override the Enter keybind handler ourselves
      'answer': [{'key': 's-escape'}],
      'toggle-exact': [{ 'key': 'c-e' }],
    },
  )
  keybinds.register_delete_keybind(prompt)
  keybinds.register_left_keybind(prompt)
  keybinds.register_right_keybind(prompt)
  keybinds.register_fuzzy_search_enter_keybind(prompt)
  keybinds.register_fuzzy_search_space_keybind(prompt)
  return prompt.execute()

def get_single_selection(
  message: str,
  choices: Sequence[Choice],
  default: DefaultChoice | None = None,
  required: bool = True,
  match_exact: bool = False,
):
  transformed_choices = [transform_choice(c, default) for c in choices]
  if default:
    prompt = inquirer.select(
      message=message,
      choices=transformed_choices,
      default=default,
      mandatory=required,
      qmark='',
      amark='',
      pointer='> ',
      marker='',
      marker_pl='',
    )
  else:
    prompt = inquirer.fuzzy(
      message=message,
      choices=transformed_choices,
      multiselect=False,
      match_exact=match_exact,
      cycle=False,
      mandatory=required,
      pointer='> ',
      marker='',
      marker_pl='',
      exact_symbol=' [Exact]',
      keybindings={
        'toggle-exact': [{ 'key': 'c-e' }],
      },
    )
    keybinds.register_delete_keybind(prompt)
    keybinds.register_left_keybind(prompt)
    keybinds.register_right_keybind(prompt)
  return prompt.execute()

def get_text_input(message: str, default: str | None = None, required: bool = True, multiline: bool = False):
  prompt = inquirer.text(
    message=message,
    default=default or '',
    mandatory=required,
    multiline=multiline,
    qmark='',
    amark='',
    vi_mode=True,
  )
  return prompt.execute()

def get_number_input(
  message: str,
  min_allowed: float | None = None,
  max_allowed: float | None = None,
  required: bool = True,
  default: float | None = None,
  float_allowed: bool = False,
) -> float | int | None:
  prompt = inquirer.number(
    message=message,
    min_allowed=min_allowed,
    max_allowed=max_allowed,
    mandatory=required,
    default=default,
    float_allowed=float_allowed,
  )
  value = prompt.execute()
  return default if value is None or value == '' else float(value) if float_allowed else int(value)

def get_confirmation(message: str, long_message: str | None = None):
  if long_message: print(long_message)
  return inquirer.confirm(
    message=message,
    default=False,
  ).execute()

def prompt_exit_or_redo(
  default: str = 'EXIT',
  redo_text: str = 'Redo',
  exit_text: str = 'Exit',
):
  choice = get_single_selection(
    message='Redo or exit?',
    choices=[(redo_text, 'REDO'), (exit_text, 'EXIT')],
    default=default,
  )
  return choice == 'REDO'

def redo_loop(
  default: str = 'EXIT',
  **prompt_kw_args,
):
  def decorator(fn: Callable):
    def wrapper(*, args: dict | None = None, initial_args: dict | None = None):
      fn(**(initial_args or args or {}))
      while redo := prompt_exit_or_redo(default=default, **prompt_kw_args):
        fn(**(args or {}))
    return wrapper
  return decorator

def loop_for_value(prompt, fn):
  while value := input(prompt):
    fn(value)

def get_required_value(prompt):
  while not (value := input(prompt)):
    print('This is required.')
  return value

def loop_inputs_to_array(prompt_str, cap: int | None = None, split_items_fn: Callable[[str], list[str]] | None = None):
  inputs = []
  while cap is None or len(inputs) < cap:
    current_input = input(prompt_str)
    if not current_input == '':
      inputs.append(current_input)
    else:
      break
  if split_items_fn:
    return [item for line_input in inputs for item in split_items_fn(line_input)]
  return inputs

def prompt_for_append_selections(
  prompt: str,
  choices: Sequence[Choice],
  default: DefaultChoice | None = None,
  allow_text_input: bool = False,
  text_input_start: bool = False,
  allow_timestamp: bool = True,
) -> str:
  choices = [('Custom Text', 'CUSTOM_TEXT')] + list(choices) if text_input_start else list(choices) + [('Custom Text', 'CUSTOM_TEXT')] if allow_text_input else choices
  if allow_timestamp: choices = list(choices) + [('Current Timestamp', 'CURRENT_TIMESTAMP')]
  selections = get_multi_selections(prompt, choices, default=default)
  if 'CUSTOM_TEXT' in selections:
    custom_text = input('Text to append: ')
    if custom_text:
      selections = [custom_text if item == 'CUSTOM_TEXT' else item for item in selections]
    else:
      selections = [item for item in selections if not item == 'CUSTOM_TEXT']
  if 'CURRENT_TIMESTAMP' in selections:
    selections = [str(int(time.time() * 1000)) if item == 'CURRENT_TIMESTAMP' else item for item in selections]
  text = ' - '.join(selections) if selections else ''
  return text

def prompt_for_folder_selections(
  prompt: str,
  choices: Sequence[Choice],
  default: DefaultChoice | None = None,
  allow_text_input: bool = True,
  text_input_start: bool = True,
  single_selection: bool = False,
  required: bool = True,
) -> str | list[str]:
  if allow_text_input: choices = ['Custom'] + list(choices) if text_input_start else list(choices) + ['Custom']
  selection_fn = get_single_selection if single_selection else get_multi_selections
  selections = selection_fn(prompt, choices, default=default, required=required)
  if single_selection: selections = [selections]
  if 'Custom' in selections:
    custom_folders = loop_inputs_to_array(
      prompt_str='Folder name: ',
      cap=1 if single_selection else None,
    )
    selections = [item for item in selections if not item == 'Custom'] + custom_folders
  return selections[0] if single_selection else selections

def prompt_for_folder(title: str, refocus_after_selection: bool = False) -> str | None:
  root = Tk()
  root.withdraw()  # Hide the root window
  folder_path = filedialog.askdirectory(title=title)
  if refocus_after_selection: utils.focus_console_window()
  return folder_path if folder_path else None

class FileTypesCategory(Enum):
  DEFAULT = 'DEFAULT'
  VIDEO = 'VIDEO'
  M3U8 = 'M3U8'
  LOG = 'LOG'
  TEXT = 'TEXT'
  JSON = 'JSON'
  JSON_AND_TEXT = 'JSON_AND_TEXT'

FILE_TYPES_MAPPING = {
  FileTypesCategory.DEFAULT: [
    ('All Files', '*.*'),
  ],
  FileTypesCategory.VIDEO: [
    ('MP4 files', '*.mp4'),
    ('MKV files', '*.mkv'),
    ('All Files', '*.*'),
  ],
  FileTypesCategory.M3U8: [
    ('M3U8 files', '*.m3u8'),
    ('All Files', '*.*'),
  ],
  FileTypesCategory.LOG: [
    ('Log files', '*.log'),
    ('Text Files', '*.txt'),
    ('All Files', '*.*'),
  ],
  FileTypesCategory.TEXT: [
    ('Text Files', '*.txt'),
    ('All Files', '*.*'),
  ],
  FileTypesCategory.JSON: [
    ('JSON files', '*.json5 *.json'),
    ('All Files', '*.*'),
  ],
  FileTypesCategory.JSON_AND_TEXT: [
    ('JSON and Text files', '*.json5 *.json *.txt'),
    ('JSON files', '*.json *.json5'),
    ('Text Files', '*.txt'),
    ('All Files', '*.*'),
  ],
}

def prompt_for_new_file_path(
  title: str | None = None,
  default_extension: str = '',
  file_types: FileTypesCategory | list[tuple[str, str]] | None = None,
  initial_dir: str | None = None,
  initial_file: str | None = None,
  refocus_after_selection: bool = False,
) -> str | None:
  file_types = file_types if file_types is not None else FileTypesCategory.DEFAULT
  if isinstance(file_types, FileTypesCategory):
    file_types = FILE_TYPES_MAPPING.get(file_types, FILE_TYPES_MAPPING[FileTypesCategory.DEFAULT])
  root = Tk()
  root.withdraw()  # Hide the root window
  file_path = filedialog.asksaveasfilename(
    title=title,
    defaultextension=default_extension,
    filetypes=file_types,
    initialdir=initial_dir,
    initialfile=initial_file,
  )
  if refocus_after_selection: utils.focus_console_window()
  return file_path if file_path else None

def prompt_fn_required(prompt_fn, retry_message='Input is required. Press Enter to try again.', **kwargs):
  while not (result := prompt_fn(**kwargs)):
    input(retry_message)
  return result

def prompt_folder_required(retry_message='Folder selection is required. Press Enter to try again.', **kwargs):
  return prompt_fn_required(
    prompt_for_folder,
    retry_message=retry_message,
    **kwargs,
  )
