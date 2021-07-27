global script_name


class ThreadX( threading.Thread ):
  def run( self ):
    name = threading.currentThread().getName()
    output ( name, 'started!' )
    while script_name:
      import random
      t = random.randint(1,10)
      log_output( name, 'sleeping for '+str(t)+' seconds...' )
      time.sleep( t )
    output (name, 'done!')


tag_color('Thread1','red')
tag_color('Thread2','green')
tag_color('Thread3','blue')
time.sleep( 1 )

th1 = ThreadX( name='Thread1' )
th1.start()
th2 = ThreadX( name='Thread2' )
th2.start()
th3 = ThreadX( name='Thread3' )
th3.start()

while script_name:
  time.sleep( 1 )
