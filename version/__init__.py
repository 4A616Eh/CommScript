
# -----------------------------------------------------------------------------
# History
# -----------------------------------------------------------------------------
#
version = 'CommScript 1.05'
#
# Version 1.00:
# - Initial Version
# Version 1.01:
# - Fix Editor Window (Modification in my_idlelib)
# Version 1.03:
# - added RTF example
# - added user_line_end and set_line_end(ln_end_str=None)
#   default line end for "sendln()" as in previous versions: \r\n
# Version 1.04
# - added input line command \\ to execute scripts
# - moved examples to scripts/examples
# - configurable fonts and sizes for input, output, and inputline
# Version 1.05
# - adapted to python3
# - using json format for saving setup and tags
# - removed xmodem support
# - uses by default encoding latin_1. Not configurable at this time.
#   No need to set default encoding in system settings.
# - fixed crash when USB serial adapter is removed while port is open
# - timeout for // search (will no longer lock for very long time if
#   search results in a lot of matches)
