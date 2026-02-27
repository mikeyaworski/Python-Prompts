# Python Prompts

## Summary

This is a set of utility functions to prompt user input on the command-line. Most of the utils are wrappers around the library InquirerPy.

InquirerPy is a nice library, primarily since it has input filtering for the list (multi-select lists especially).

The downside of InquirerPy is that the customization options are pretty limited at a surface level, and some of the default behavior is clunky. As a result, I've created some wrapper functions that patch up the clunky aspects and overwrite some of the internal key handlers.

These wrappers are very opinionated based on what I think is the smoothest experience.

## Installation

Add the following to your `requirements.txt` file and run `pip install -r requirements.txt`.

```
git+ssh://git@github.com:mikeyaworski/Python-Prompts.git@master#egg=prompts

# Editable version (for local development)
# -e Absolute/Path/To/Python-Prompts
```

The project name is called `prompts`, so you would import it like:

```
import prompts
prompts.get_multi_selections(...)
```
