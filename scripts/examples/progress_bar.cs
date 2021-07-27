
# this is a demonstration, how the progress bar in the status line
# can be updated... please not that the progress bar is used for 
# xmodem transfers, so updating during xmodem should not be done...

global script_name

output( "" )
output( "" )
output( "SCRIPT", script_name, "IS RUNNING!" )

for i in range(101):
  update_progress( i )
  if not script_name: 
    output( "SCRIPT HAS BEEN STOPPED!!" )
    break
  time.sleep(0.2)
  
if i == 100:
  output( "SCRIPT FINISHED." )
output( "" )
output( "" )

