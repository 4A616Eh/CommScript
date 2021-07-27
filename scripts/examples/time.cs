
# this script shows a ticking clock in the status line

global script_name         # if empty, script must quit!

while script_name:         # script will stop when empty!
  t = time.strftime( 'local time: %H:%M:%S', time.localtime( time.time() ) )
  update_status_line( t )  # set the new text in the status line
  time.sleep(0.5)          # wait for 0.5 seconds

