
# This script shows how to open a second RS-232 port and log the received data 
# from the second port with time stamp (similar to data received from the
# regular port). Here, a separate thread is used to catch the data on port 2, 
# so that the script loop could still use processing data just like in other
# examples... Data from the second port will be indicated by -P2 after the
# time stamp.
# Please note that due to concurrency and scheduling, data could not come out
# exactly in the order you might expect if on both ports data is received 
# at about the same time!


global script_name
global script_data_handler
global wait

global my_open_port, my_close_port

import sys

wait_str = None
waiting = False

if sys.platform=='win32':
    my_com_port = '\\\\.\\COM3'   #  <== PLEASE SET PORT NUMBER HERE!
elif sys.platform=='linux2':
    my_com_port = '/dev/ttyUSB0'  #  <== PLEASE SET PORT NUMBER HERE!

my_speed = 9600                   #  <== PLEASE SET BAUD RATE HERE!
my_tty = None

def my_open_port():
  global my_tty, my_com_port, my_speed
  try:
    if not my_tty:
      my_tty = SerialPort( my_com_port, 1000, my_speed )
  except:
    my_tty = None  
  output_str( 'open my_tty:', my_tty )

def my_close_port():
  global my_tty
  if my_tty:
    del my_tty
    my_tty = None
  output_str( 'close my_tty:', my_tty )


# processing port 1 data
# ----------------------

def my_data_handler( line ):
  global wait_str, waiting
  if waiting and wait_str:
    for strg in wait_str:
      if line[:len(strg)] == strg:
        wait_str = line
        waiting = False
  
def wait( s, timeout ):
  global wait_str, waiting
  if type(s) == type('str'):
    wait_str = [ s ]
  else:
    wait_str = s
  wait_timer = 0
  waiting = True
  while script_name and waiting and (not wait_timer > timeout) :
    wait_timer += 1
    time.sleep(0.1)
  ok = not waiting
  waiting = False
  return ok


# processing port 2 data
# ----------------------

linebuffer = ''
th1_running = False

class Thread1( threading.Thread ):
  def run( self ):
    global my_tty, linebuffer, th1_running
    th1_running = True
    output ('Thread1 started!')
    while th1_running:
      if my_tty != None:
        while ( my_tty.inWaiting() > 0 ):
          ch = my_tty.read( 1 )
          linebuffer += ch
          if (ch == '\n') or (ch == '\r'):
            linebuffer = linebuffer.replace('\r','').replace('\n','')
            if linebuffer:
              log_output( 'P2', linebuffer )
              linebuffer = ''
        time.sleep( 0.1 )
    output ('Thread1 done!')


# script main program
# -------------------

def script_main():
  global th1_running, my_tty, Thread1
  my_open_port()
  if my_tty:
    th1 = Thread1( name='thread1' )
    th1.start()
  while script_name:
    # ...
    # do communication through port 1 here using send() and wait()
    # will not disturb receiving from port 2!
    # ...
    # if required, you could also write to the 2nd port with:
    # my_tty.write( <string> )
    # ...
    time.sleep( 0.1 )
  if my_tty:
    th1_running = False
    th1.join()
    del my_tty

  
script_data_handler = my_data_handler


output_str( '\n\nUSING 2 PORTS... EXAMPLE SCRIPT RUNNING!\n' )
script_main()
output_str( '\n\nSCRIPT FINISHED!\n' )

