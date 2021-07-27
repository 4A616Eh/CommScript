
# this is just some hello world program that prints hello world together
# with a counter to the output area... important for loops is to exit when
# the script name is empty!

global script_name

output( "" )
output( "" )
output( "SCRIPT", script_name, "IS RUNNING!" )

cnt = 0

while script_name:
  output( "Hello World", cnt, "!" )
  cnt += 1
  time.sleep(1)

output( "SCRIPT HAS BEEN STOPPED!!" )
output( "" )
output( "" )


