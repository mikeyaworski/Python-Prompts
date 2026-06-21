on run argv
  set promptText to (item 1 of argv) as text
  set defaultName to (item 2 of argv) as text
  set defaultLoc to (item 3 of argv) as text
  if defaultLoc is not "" then
    set defaultLoc to POSIX file defaultLoc
    set chosen to choose file name with prompt promptText default name defaultName default location defaultLoc
  else
    set chosen to choose file name with prompt promptText default name defaultName
  end if
  return POSIX path of chosen
end run
