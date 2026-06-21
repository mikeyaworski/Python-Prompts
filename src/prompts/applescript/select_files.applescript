on run argv
  set promptText to (item 1 of argv) as text
  set theFiles to choose file with prompt promptText with multiple selections allowed
  set outStr to ""
  repeat with f in theFiles
    set outStr to outStr & POSIX path of f & linefeed
  end repeat
  return outStr
end run
