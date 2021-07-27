
# -*- coding: cp1252 -*-


global str_list, ex, wait, wait_str
global script_name, script_data_handler
global re_action, add_re_action, del_re_action


# ----------------------------------------------------------------------------
# handling data, including possibilty to define callbacks for matches of
# regular expression applied to incoming data. The callback function must
# take two arguments: 1) the entire received line, and 2) a match object
# of which functions like .group may be used...
# ----------------------------------------------------------------------------

def str_list( s ):
  if type(s) == type('str'): return [ s ]
  else: return s 

def ex():
  output_str( '\n\n!! EXCEPTION !!' )
  output_str( 'Traceback (most recent call last):' )
  for line in traceback.format_tb(sys.exc_info()[2]):
    output_str( line )
  output_str( sys.exc_info()[0] )
  output_str( sys.exc_info()[1] )

wait_str = None
waiting = False
re_action = {}

def add_re_action( name, regexp, cbk_f ):
  import re
  global re_action
  p = re.compile( regexp )
  re_action[ name ] = ( p, cbk_f )
  
def del_re_action( name ):
  global re_action
  try:
    re_action.pop( name )
  except: pass  

def my_data_handler( line ):
  global wait_str, waiting
  global re_action
  try:
    if re_action:
      for name in re_action:
        p, f = re_action[name]
        m = p.match( line )
        if m: f( line, m )
    if waiting and wait_str:
      for strg in wait_str:
        if line[:len(strg)] == strg:
          wait_str = line
          waiting = False
  except:
    ex()
      
def wait( s, timeout ):
  global wait_str, waiting
  wait_str = str_list( s )
  wait_timer = 0
  waiting = True
  while script_name and waiting and (not wait_timer > timeout) :
    wait_timer += 1
    time.sleep(0.1)
  ok = not waiting
  waiting = False
  return ok

script_data_handler = my_data_handler


# ----------------------------------------------------------------------------
# main program
# Note: this is a very basic example. You can match much more complicated
# things than just 'OK'... Please see the Regular Expression HOWTO included
# in the documentation!
# ----------------------------------------------------------------------------

global OK_counter, re_action_OK
OK_counter = 0

# call back function
def re_action_OK( line, m ):
  global OK_counter
  OK_counter += 1
  output( 're_action_OK: OK_counter =', OK_counter )

def main():
  global script_name
  match_expr = 'OK'
  add_re_action( 'REACT_OK', match_expr, re_action_OK )
  while script_name:
    time.sleep(0.5)


main()

