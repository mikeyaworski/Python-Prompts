'''
This includes a lot of manipulation of the internal state management for InquirerPy, which I found in the source code.
The library has very limited options for key behaviors, so this is necessary for the customization I want.
https://inquirerpy.readthedocs.io/en/latest/pages/kb.html#customising-keybindings
https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/key_bindings.html#list-of-special-keys
https://github.com/kazhala/InquirerPy/blob/714d9068896c1a1f9f4d1354f43f922cd5cfe16d/InquirerPy/prompts/fuzzy.py
'''

def register_delete_keybind(prompt):
  '''Clear search input'''
  @prompt.register_kb('delete')
  def _(event):
    if event.app.current_buffer.text == '':
      event.app.exit(result=None)
    else:
      event.app.current_buffer.text = ''
      event.app.current_buffer.cursor_position = 0

def register_left_keybind(prompt):
  '''Deselect the current option'''
  @prompt.register_kb('left')
  def _(event):
    if prompt.content_control.choice_count > 0:
      prompt._set_choice_enabled(prompt.content_control.selection['index'], False)

def register_right_keybind(prompt):
  '''Select the current option'''
  @prompt.register_kb('right')
  def _(event):
    if prompt.content_control.choice_count > 0:
      prompt._set_choice_enabled(prompt.content_control.selection['index'], True)

def register_fuzzy_search_enter_keybind(prompt):
  '''
  If there is search input, clear the input and select the current option.
  If there is no search input, complete the prompt with whatever options are currently selected.
  The default behavior would be to select the current option and complete the prompt, even if nothing is selected.
  '''
  @prompt.register_kb('enter')
  def _(event):
    buffer = event.app.current_buffer
    no_choices_selected = all(not choice['enabled'] for choice in prompt.content_control.choices)
    choices_selected = not no_choices_selected
    if not buffer.text and no_choices_selected:
      if prompt._mandatory:
        prompt._set_error(prompt._mandatory_message)
      else:
        event.app.exit(result=[])
    elif not buffer.text and choices_selected:
      prompt._handle_enter(event)
    elif buffer.text:
      if prompt.content_control.choice_count > 0:
        prompt._set_choice_enabled(prompt.content_control.selection['index'], True)
      event.app.current_buffer.text = ''
      event.app.current_buffer.cursor_position = 0

def register_fuzzy_search_space_keybind(prompt):
  '''
  If there is search input, toggle the current option (searching for whitespace makes no sense).
  If there is already search input, they may want to include whitespace, so just register it as normal input.
  '''
  @prompt.register_kb('space')
  def _(event):
    buffer = event.app.current_buffer
    if buffer.text == '':
      prompt._handle_toggle_choice(event)
    else:
      buffer.text += ' '
      buffer.cursor_position += 1

def register_move_up_keybind(prompt):
  @prompt.register_kb('c-up')
  def _(event):
    index = prompt.content_control.selected_choice_index
    if index > 0:
      choices = prompt.content_control.choices
      choices[index - 1], choices[index] = (
        choices[index],
        choices[index - 1],
      )
      prompt.content_control.selected_choice_index = index - 1
      event.app.invalidate()

def register_move_down_keybind(prompt):
  @prompt.register_kb('c-down')
  def _(event):
    index = prompt.content_control.selected_choice_index
    choices = prompt.content_control.choices
    if index < len(choices) - 1:
      choices[index], choices[index + 1] = (
        choices[index + 1],
        choices[index],
      )
      prompt.content_control.selected_choice_index = index + 1
      event.app.invalidate()
