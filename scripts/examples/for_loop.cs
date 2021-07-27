
# this script just runs a for loop from 0...9 and then quits...
# it will print some values to the output area...

global script_name

output( "" )
output( "" )
output( "SCRIPT", script_name, "IS RUNNING!" )

for i in range(10): 
  output( "i =", i, "  i*7 =", i*7 )

output( "SCRIPT", script_name, "IS FINISHED!" )
output( "" )
output( "" )

