from InquirerPy import inquirer
from tkinter import filedialog, Tk
from enum import Enum
from . import keybinds

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

def get_multi_selections(message: str, choices: list[Choice], default: DefaultChoice | None = None, required: bool = False):
  choices = [transform_choice(c, default) for c in choices]
  prompt = inquirer.fuzzy(
    message=message,
    choices=choices,
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

def get_single_selection(message: str, choices: list[Choice], default: DefaultChoice | None = None, required: bool = True):
  choices = [transform_choice(c, default) for c in choices]
  if default:
    prompt = inquirer.select(
      message=message,
      choices=choices,
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
      choices=choices,
      multiselect=False,
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

def get_number_input(
  message: str,
  min_allowed: float | None = None,
  max_allowed: float | None = None,
  required: bool = True,
  default: float | None = None,
  float_allowed: bool = False,
):
  prompt = inquirer.number(
    message=message,
    min_allowed=min_allowed,
    max_allowed=max_allowed,
    mandatory=required,
    default=default,
    float_allowed=float_allowed,
  )
  return prompt.execute()

def get_confirmation(message: str, long_message: str | None = None):
  if long_message: print(long_message)
  return inquirer.confirm(
    message=message,
    default=False,
  ).execute()

def prompt_exit_or_redo(default: str = 'EXIT'):
  choice = get_single_selection(
    message='Redo or exit?',
    choices=[('Redo', 'REDO'), ('Exit', 'EXIT')],
    default=default,
  )
  return choice == 'REDO'

def redo_loop(fn, default: str = 'EXIT', args: dict = {}, initial_args: dict = {}):
  fn(**(initial_args or args))
  while redo := prompt_exit_or_redo(default=default):
    fn(**(args))

def loop_for_value(prompt, fn):
  while value := input(prompt):
    fn(value)

def get_required_value(prompt):
  while not (value := input(prompt)):
    print('This is required.')
  return value

def loop_inputs_to_array(prompt_str, cap: int | None = None):
  inputs = []
  while cap is None or len(inputs) < cap:
    current_input = input(prompt_str)
    if not current_input == '':
      inputs.append(current_input)
    else:
      break
  return inputs

def prompt_for_append_selections(
  prompt: str,
  choices: list[Choice],
  default: DefaultChoice | None = None,
  allow_text_input: bool = False,
  text_input_start: bool = False,
) -> str:
  choices = ['Custom Text'] + choices if text_input_start else choices + ['Custom Text'] if allow_text_input else choices
  selections = get_multi_selections(prompt, choices, default=default)
  has_custom_text = 'Custom Text' in selections
  if has_custom_text:
    custom_text = input('Text to append: ')
    if custom_text:
      selections = [custom_text if item == 'Custom Text' else item for item in selections]
    else:
      selections = [item for item in selections if not item == 'Custom Text']
  text = ' - '.join(selections) if selections else ''
  return text

def prompt_for_folder_selections(
  prompt: str,
  choices: list[Choice],
  default: DefaultChoice | None = None,
  allow_text_input: bool = True,
  text_input_start: bool = True,
  single_selection: bool = False,
  required: bool = True,
) -> str | list[str]:
  if allow_text_input: choices = ['Custom'] + choices if text_input_start else choices + ['Custom']
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

def prompt_for_folder(message: str) -> str | None:
  root = Tk()
  root.withdraw()  # Hide the root window
  folder_path = filedialog.askdirectory(title=message)
  return folder_path if folder_path else None

def prompt_folder_required(prompt_folder_fn, retry_message='Folder is required. Press Enter to try again.'):
  while not (folder := prompt_folder_fn()):
    input(retry_message)
  return folder

class FileTypesCategory(Enum):
  DEFAULT = 'DEFAULT'
  VIDEO = 'VIDEO'
  M3U8 = 'M3U8'
  LOG = 'LOG'
  TEXT = 'TEXT'

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
}

def prompt_for_new_file_path(
  message: str,
  default_extension: str = '',
  file_types: FileTypesCategory | list[tuple[str, str]] | None = None,
  initial_dir: str | None =None,
  initial_file: str | None =None,
) -> str | None:
  file_types = file_types if file_types is not None else FileTypesCategory.DEFAULT
  if isinstance(file_types, FileTypesCategory):
    file_types = FILE_TYPES_MAPPING.get(file_types, FILE_TYPES_MAPPING[FileTypesCategory.DEFAULT])
  root = Tk()
  root.withdraw()  # Hide the root window
  file_path = filedialog.asksaveasfilename(
    title=message,
    defaultextension=default_extension,
    filetypes=file_types,
    initialdir=initial_dir,
    initialfile=initial_file
  )
  return file_path if file_path else None
