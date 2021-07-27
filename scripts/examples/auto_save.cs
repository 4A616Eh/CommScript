
# demonstration how to call a function periodically from the main thread.
# this script needs pyTkTerm version 2.01 or higher. Please be careful
# not to block main thread, otherwise the GUI will no longer work, and
# you most likely will not be able to exit the program without help of
# the Windows operating system ;-)
# this script actually is finished before the result is actually available.
# if the further actions in the script thread depend on the result, you
# will need to implement some kind of wait in the script thread...

# this script will start auto-saving every 5 minutes, then exits. Other
# scripts may run then! To stop auto-saving close the pyTkTerm program

global save_fun, save
  
def save_fun():
  log_output( 'save', 'auto saving...' )
  save()
  log_output( 'save', 'done!' )
  root.after( 5*60*1000, save_fun )


fun_call( save_fun )

