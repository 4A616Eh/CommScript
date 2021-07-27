
global script_name

output( "" )
output( "" )
output( "SCRIPT", script_name, "IS RUNNING!" )

for i in range(256): 
  output( 'Char', i, ':', chr(i) )

output( "SCRIPT", script_name, "IS FINISHED!" )
output( "" )
output( "" )

