on run argv
  set promptText to ""
  if (count of argv) ≥ 1 then
    set promptText to item 1 of argv
  end if
  return POSIX path of (choose folder with prompt promptText)
end run
