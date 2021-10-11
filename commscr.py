
import version

from tkinter import *
from tkinter.commondialog import Dialog
from tkinter.messagebox import showinfo,showwarning,showerror,askquestion,askokcancel,askyesno,askretrycancel

from queue import Queue

from SerialPort_standard import *
import time
import threading
import re
import os
import traceback
import binascii

import my_idlelib
import my_idlelib.editor
import my_idlelib.filelist

import glob
import json

PLATFORM_UNKNOWN = 0
PLATFORM_LINUX = 1
PLATFORM_WIN   = 2
global platform
platform = PLATFORM_UNKNOWN

import sys

if sys.platform=='linux2':
    platform = PLATFORM_LINUX
if sys.platform=='win32':
    platform = PLATFORM_WIN

if platform == PLATFORM_UNKNOWN:
    sys.exit('Unsupported platform!')

def ENC(s):
  if (type(s) == type(bytes)):
    return s.encode('latin_1')
  else:
    return s

# -----------------------------------------------------------------------------
# Useful tools...
# -----------------------------------------------------------------------------

def tk_get_index_from_position(pos):
    return "1.0 + %d chars" % pos
    
def ex():
  output_str( '\n>>> Exception <<<' )
  output_str( sys.exc_info()[0] )  
  output_str( sys.exc_info()[1] )


def base( r1, r2, num, fill=None ):
  # use base 10 as a pivot to go from base r1 to r2.
  import string
  digits=""
  for j in range(0,10):         #We collect the ascii characters we want to use
    digits = digits + chr(j+48)
  for j in range(10,16):
    digits = digits + chr(j+55)
  output(digits)  
  num1 = str(num).upper()
  ln  = len(num1)
  dec = 0
  for j in range(ln):
    try:
      asci = string.index(digits,num1[j])
    except:
      return 'ERROR'
    if asci >= r1: return 'ERROR'
    temp = r1**(ln-j-1)         #Get decending powers of the decimal encoded
    dec += asci*temp            #Convert the num in r1 to decimal
  RDX = ""                      #Init the storage string
  j=-1
  dec2=dec
  while dec2:                   #get number of digits in decimal
    dec2 = dec2 / r2
    j = j+1
  while j >= 0:
    pwr = r2**j                 #This is going from base 10 to another base
    Q   = dec // pwr            #converting decimal number to r2 which in effect
    dec = dec % pwr             #converting num in base r1 to a number in base r2
    RDX = RDX + digits[Q]
    j-=1
  if fill:
    while len(RDX) < fill:
      RDX = '0' + RDX
  return RDX

def is_bin( num ): return base( 2, 2, num ) != 'ERROR'
def is_dec( num ): return base( 10, 10, num ) != 'ERROR'
def is_hex( num ): return base( 16, 16, num ) != 'ERROR'

def bin2hex( num, fill=None ): return base( 2, 16, num, fill )
def hex2bin( num, fill=None ): return base( 16, 2, num, fill )
def bin2dec( num, fill=None ): return base( 2, 10, num, fill )
def dec2bin( num, fill=None ): return base( 10, 2, num, fill )
def dec2hex( num, fill=None ): return base( 10, 16, num, fill )
def hex2dec( num, fill=None ): return base( 16, 10, num, fill )


# -----------------------------------------------------------------------------
# Drop-Down
# -----------------------------------------------------------------------------

class DropDown( Frame ):
  def __init__( self, parent, var, choiceList ):
    Frame.__init__( self, parent, relief=RAISED, borderwidth=2 )
    self.var = var
    self.choiceList = choiceList
    self.__index = 0
    self.__mb = Menubutton( self, text=choiceList[0] )
    self.__mb.grid( row=0, column=0 )
    self.__menu = Menu( self.__mb, tearoff=0 )
    self.create_menu( choiceList )
    self.__mb['menu'] = self.__menu

  def create_menu( self, choiceList ):
    self.__rbList = []
    for i in range( len(choiceList) ):
      choice = choiceList[i]
      def handler( s=self, i=i ):
        self.__index = i
        self.__mb['text'] = self.var.get()
      rb = self.__menu.add_radiobutton( label=choice,
        value=choice, variable=self.var, command=handler )
      self.__rbList.append( rb )

  def update_menu( self, choiceList ):
    self.__menu.delete( 0, END )
    self.create_menu( choiceList )
    
  def set( self, i ):
    value = self.choiceList[i]
    self.var.set( self.choiceList[i] )
    self.__mb['text'] = self.choiceList[i]
    self.__index = i

  def get( self ):
    return self.__index


# -----------------------------------------------------------------------------
# Progress Bar
# -----------------------------------------------------------------------------

class ProgressBarView:
  def __init__( self, master=None, orientation='horizontal',
      min=0, max=100, width=100, height=None, doLabel=1, appearance=None,
      fillColor=None, background=None, labelColor=None, labelFont=None,
      labelText='', labelFormat='%d%%', value=0.1, bd=2 ):
    # preserve various values
    self.master = master
    self.orientation = orientation
    self.min = min
    self.max = max
    self.doLabel = doLabel
    self.labelText = labelText
    self.labelFormat = labelFormat
    self.value = value
    if (fillColor == None) or (background == None) or (labelColor == None):
      # We have no system color names under linux. So use a workaround.
      #btn = Button(font=labelFont)
      btn = Button( master, text='0', font=labelFont )
      if fillColor == None:
        fillColor = btn['foreground']
      if background == None:
        background = btn['disabledforeground']
      if labelColor == None:
        labelColor = btn['background']
    if height == None:
      l = Label( font=labelFont )
      height = l.winfo_reqheight()
    self.width = width
    self.height = height
    self.fillColor = fillColor
    self.labelFont = labelFont
    self.labelColor = labelColor
    self.background = background
    self.frame = Frame( master, relief=appearance, bd=bd, width=width, height=height )
    self.canvas = Canvas( self.frame, bd=0,
      highlightthickness=0, background=background, width=width, height=height )
    self.scale=self.canvas.create_rectangle( 0, 0, width, height, fill=fillColor )
    self.label=self.canvas.create_text( width / 2, height / 2,
      text=labelText, anchor=CENTER, fill=labelColor, font=self.labelFont )
    self.canvas.pack( fill=BOTH )
    self.update()
    self.canvas.bind( '<Configure>', self.onResize ) # monitor size changes

  def onResize( self, event ):
    if (self.width == event.width) and (self.height == event.height):
      return
    # Set new sizes
    self.width = event.width
    self.height = event.height
    # Move label
    self.canvas.coords( self.label, event.width/2, event.height/2 )
    # Display bar in new sizes
    self.update()

  def updateProgress( self, newValue, newMax=None ):
    if newMax:
      self.max = newMax
    self.value = newValue
    self.update()

  def pack( self, *args, **kw ):
    self.frame.pack( *args, **kw )

  def update( self ):
    # Trim the values to be between min and max
    value = self.value
    if value > self.max:
      value = self.max
    if value < self.min:
      value = self.min
    # Adjust the rectangle
    if self.orientation == 'horizontal':
      self.canvas.coords( self.scale, 0, 0,
        float(value) / self.max * self.width, self.height )
    else:
      self.canvas.coords( self.scale, 0,
        self.height - (float(value) / self.max*self.height),
        self.width, self.height )
    # And update the label
    if self.doLabel:
      if value:
        if value >= 0:
          pvalue = int( (float(value) / float(self.max)) * 100.0 )
        else:
          pvalue = 0
        self.canvas.itemconfig( self.label, text=self.labelFormat % pvalue )
      else:
        self.canvas.itemconfig( self.label, text='' )
    else:
      self.canvas.itemconfig( self.label, text=self.labelFormat %
        self.labelText )
    self.canvas.update_idletasks()


# -----------------------------------------------------------------------------
# Dialogs for Opening and Saving Files
# -----------------------------------------------------------------------------

class _Dialog( Dialog ):
  global setup
  def __init__(self, setup_path_file_names=('path','file'), master=None, **options):
    self.master = master
    self.path, self.file = setup_path_file_names
    try:
      options['initialdir'] = setup[self.path]
      options['initialfile'] = setup[self.file]
    except: pass  
    self.options = options
  def _fixresult( self, widget, result ):
    if result:
      try:
        result = result.string
      except AttributeError:
        pass
      setup[self.path], setup[self.file] = os.path.split( result )
      self.options['initialdir'] = setup[self.path]
      self.options['initialfile'] = setup[self.file]
    self.filename = result
    return result
  def _fixoptions( self ):
    try:
      # make sure 'filetypes' is a tuple
      self.options['filetypes'] = tuple(self.options['filetypes'])
    except KeyError:
      pass

class Open( _Dialog ):
  command = 'tk_getOpenFile'

class SaveAs( _Dialog ):
  command = 'tk_getSaveFile'


# -----------------------------------------------------------------------------
# Global Variables
# -----------------------------------------------------------------------------

init_ports = ['OFF'] + list(['COM'+str(x) for x in range(10)])[1:]
init_speeds = list(map(str,[921600,460800,230400,115200,57600,38400,19200,9600,4800,2400]))
init_params = [x+y+z for x in ['8','7'] for y in ['N','O','E','M','S'] for z in ['1','2']]
init_flowctrls = ['None', 'Xon/Xoff', 'Hardware']
init_ts_format = '%H:%M:%S'
init_outputFont = ('Courier', 16, 'bold')
init_inputFont = ('Arial', 12, '')
init_inputlineFont = ('Courier', 16, 'bold')
init_inputWidth = 25
init_inputlineWidth = 60
init_outputWidth = 40
init_outputHeight = 20

d = None
setup = dict( scroll_mode=True, dwl_path='.', dwl_file='',
              in_path='.', in_file='', out_path='.', out_file='',
              title=version.version, v=version.version[-5:], i=None, geometry=None,
              port=init_ports[0], ports=init_ports,
              speed=init_speeds[0], speeds=init_speeds,
              param=init_params[0], params=init_params,
              flowctrl=init_flowctrls[0], flowctrls=init_flowctrls,
              ts_format=init_ts_format, autostart=None,
              outputFont = init_outputFont, inputFont = init_inputFont,
              inputlineFont = init_inputlineFont,
              inputWidth = init_inputWidth, inputlineWidth = init_inputlineWidth,
              outputWidth = init_outputWidth, outputHeight = init_outputHeight,
              startup_path='.', tcolors={ 'hit':(None,'yellow'), 'hit0':(None,'orange') } )
s_th = None
 
inbuffer = ''
inlines = []
tty = None

mutex = threading.RLock()

AT_CMD = 1
USER_SPLIT = 3
BINARY = 4

serial_mode = AT_CMD
user_split_str = '\n'

def set_serial_mode( mode, split_str=None ):
  global serial_mode, user_split_str
  if mode in [ AT_CMD, USER_SPLIT ]:
    serial_mode = mode
    if split_str:
      user_split_str = split_str

user_line_end = '\r\n'

def set_line_end( ln_end_str=None ):
  global user_line_end
  user_line_end = ln_end_str


root = Tk()


# -----------------------------------------------------------------------------
# GUI updates for main window elements from SerialThread or ScriptThread
# -----------------------------------------------------------------------------

## functions to be called from program (script thread or serial thread)
## or input line (main thread) follow...

def set_title( text ):
  global gui_todo, setup
  mutex.acquire()
  setup['title'] = text
  gui_todo += [ ["TI", text] ]
  mutex.release()

def update_status_line( text ):
  global gui_todo
  mutex.acquire()
  gui_todo += [ ["SL", text] ]
  mutex.release()

def update_button_run( text ):
  global gui_todo
  mutex.acquire()
  gui_todo += [ ["BS", text] ]
  mutex.release()

def update_progress( percent ):
  global gui_todo
  mutex.acquire()
  gui_todo += [ ["PB", percent] ]
  mutex.release()

def update_update_progress( percent ):
  global gui_todo
  mutex.acquire()
  gui_todo += [ ["PBU", percent] ]
  mutex.release()

def join_script_thread():
  global gui_todo
  mutex.acquire()
  gui_todo += [ ["JST"] ]
  mutex.release()

def edit( filename, line=None ):
  global gui_todo
  if filename:
    mutex.acquire()
    gui_todo += [ ["ED", filename, line] ]
    mutex.release()

def edit_close( filename ):
  global gui_todo
  if filename:
    mutex.acquire()
    gui_todo += [ ["EDC", filename] ]
    mutex.release()

def fun_call( f, param=None, result_callback=None ):
  global gui_todo
  mutex.acquire()
  gui_todo += [ ["FUN", f, param, result_callback] ]
  mutex.release()

  
## processing of update requests in MainThread

gui_todo = []

def update_gui():
  global d, gui_todo
  mutex.acquire()
  if gui_todo != []:
    for msg in gui_todo:
      if msg[0] == "PB":
        d.bar.updateProgress( msg[1] )  
      elif msg[0] == "PBU":
        d.u.bar.updateProgress( msg[1] )  
      elif msg[0] == "TI":
        d.top.title( msg[1] )
        d.top.iconname( msg[1] )
      elif msg[0] == "SL":
        sv_status.set( msg[1] )
      elif msg[0] == "BS":
        if d.button_run: d.button_run['text'] = msg[1]
      elif msg[0] == "JST":
        global script_th
        if script_th:
          script_th.join()
          script_th = None 
        if d.button_run: d.button_run['text'] = "Run..."
      elif msg[0] == "ED":
        edit = d.flist.open( msg[1] )
        edit.set_close_hook( edit.close_hook )
        if msg[2]: d.flist.gotofileline( msg[1], msg[2] )
      elif msg[0] == "EDC":
        edit = d.flist.close( msg[1] )
      elif msg[0] == "FUN":
        try:
          if not msg[2] is None:
            result = msg[1]( msg[2] )
          else:
            result = msg[1]()
          if msg[3]: msg[3]( result )
        except: pass  
  gui_todo = []  
  mutex.release()
  root.after(50, update_gui)

update_gui()


# -----------------------------------------------------------------------------
# GUI Support For Scripts...
# -----------------------------------------------------------------------------

## Communication queues between the threads
q_put = Queue()
q_get = Queue()

script_dialog_active = False

def show_ask(func):
  title, message = q_put.get()
  answer = func(title, message)
  q_get.put(answer)

def show_dialog(func):
  sn, t, f = q_put.get()
  answer = func(setup_path_file_names=sn, filetypes=f, title=t).show()
  q_get.put(answer)

def _showinfo(event=None): show_ask(showinfo)
def _showwarning(event=None): show_ask(showwarning)
def _showerror(event=None): show_ask(showerror)
def _askquestion(event=None): show_ask(askquestion)
def _askokcancel(event=None): show_ask(askokcancel)
def _askyesno(event=None): show_ask(askyesno)
def _askretrycancel(event=None): show_ask(askretrycancel)
def _dialogopen(event=None): show_dialog(Open)
def _dialogsaveas(event=None): show_dialog(SaveAs)

ev_showinfo = '<<ShowInfo>>'
ev_showwarning = '<<ShowWarning>>'
ev_showerror = '<<ShowError>>'
ev_askquestion = '<<AskQuestion>>'
ev_askokcancel = '<<AskOkCancel>>'
ev_askyesno = '<<AskYesNo>>'
ev_askretrycancel = '<<AskRetryCancel>>'
ev_dialogopen = '<<DialogOpen>>'
ev_dialogsaveas = '<<DialogSaveAs>>'

root.bind(ev_showinfo, _showinfo)
root.bind(ev_showwarning, _showwarning)
root.bind(ev_showerror, _showerror)
root.bind(ev_askquestion, _askquestion)
root.bind(ev_askokcancel, _askokcancel)
root.bind(ev_askyesno, _askyesno)
root.bind(ev_askretrycancel, _askretrycancel)
root.bind(ev_dialogopen, _dialogopen)
root.bind(ev_dialogsaveas, _dialogsaveas)

def script_show_ask(event, title, message):
  global script_dialog_active
  if threading.currentThread().getName() == 'ScriptThread':
    script_dialog_active = True
    q_put.put( (title, message) )
    root.event_generate(event, when='tail')
    result = q_get.get()
    script_dialog_active = False
    return result
  else: print(f'ERROR: function to generate {event} event only allowed in script!')

def script_show_dialog(event, setup_names, title, filetypes):
  global script_dialog_active
  if threading.currentThread().getName() == 'ScriptThread':
    script_dialog_active = True
    q_put.put( (setup_names, title, filetypes) )
    root.event_generate(event, when='tail')
    result = q_get.get()
    script_dialog_active = False
    return result
  else: print(f'ERROR: function to generate {event} event only allowed in script!')

## functions to be called from a script:
def msgbox_showinfo(title, message): return script_show_ask(ev_showinfo, title, message)
def msgbox_showwarning(title, message): return script_show_ask(ev_showwarning, title, message)
def msgbox_showerror(title, message): return script_show_ask(ev_showerror, title, message)
def msgbox_askquestion(title, message): return script_show_ask(ev_askquestion, title, message)
def msgbox_askokcancel(title, message): return script_show_ask(ev_askokcancel, title, message)
def msgbox_askyesno(title, message): return script_show_ask(ev_askyesno, title, message)
def msgbox_askretrycancel(title, message): return script_show_ask(ev_askretrycancel, title, message)
def dialog_open(setup_names, title, filetypes): return script_show_dialog(ev_dialogopen, setup_names, title, filetypes)
def dialog_saveas(setup_names, title, filetypes): return script_show_dialog(ev_dialogsaveas, setup_names, title, filetypes)

# -----------------------------------------------------------------------------
# Tag Color Managment
# -----------------------------------------------------------------------------

def tag_color_fc( params ):
  global setup
  if params[1]:
    d.output.tag_configure( params[0], foreground=params[1] )
  if params[2]:
    d.output.tag_configure( params[0], background=params[2] )
  (setup['tcolors'])[params[0]] = (params[1],params[2])
  
def tag_color( tag_name, fg_color=None, bg_color=None ):
  fun_call( tag_color_fc, (tag_name,fg_color,bg_color) )

def tag_reconfigure():
  global setup
  c = setup['tcolors']
  l = [(x,c[x][0],c[x][1]) for x in list(c.keys())]
  list(map( lambda x:fun_call(tag_color_fc,x), l ))
  
def tag_color_del_fc( tag_name ):
  global setup
  try:
    (setup['tcolors']).pop(tag_name)
    d.output.tag_remove( tag_name, '1.0', END )
  except KeyError:
    pass
  
def tag_color_delete( tag_name ):
  fun_call( tag_color_del_fc, tag_name )

def check_tag_info( list ):
  try:
    temp = list[-1]
    if temp['output_tag_info']:
      list.pop()
      return temp
  except:
    return None

def tag( tag_name ):
  return {'output_tag_info':True, 'tag':tag_name}

def get_tags():
  result = { }
  for t in d.output.tag_names():
    result[t] = tuple(map(str,d.output.tag_ranges( t )))
  return result

def set_tags( t_dict ):
  for t in list(t_dict.keys()):
    l = list( t_dict[t] )
    while len( l ) > 1:
      d.output.tag_add( t, l.pop(0), l.pop(0) )


output_todo = []

def output(*obj):
  global output_todo
  line = ''; lst = list( obj );
  tag_info = check_tag_info( lst )
  for l in lst:
    if line: line += ' '
    r = repr( l )
    if r[0] in [ '\'', '"' ]: r = r[1:][:-1]
    line += r
  line += '\n'
  mutex.acquire()
  output_todo += [ (tag_info,line) ]
  mutex.release()

def output_str(*obj):
  global output_todo
  line = ''; lst = list( obj );
  tag_info = check_tag_info( lst )
  for l in lst:
    if line: line += ' '
    line += str(l)
  line += '\n'
  mutex.acquire()
  output_todo += [ (tag_info,line) ]
  mutex.release()

def log_filter_none( str ):
  return str

def log_filter_hex( str ):
  return binascii.hexlify( str )

def log_filter_set( f ):
  global log_filter
  log_filter = f

log_filter = log_filter_none

def log_tsf_set( format=None ):
  global setup
  setup['ts_format'] = format

def log_output( tag_name, str ):
  global log_filter
  if setup['ts_format']:
    time_format = '[' + setup['ts_format']
    if tag_name: time_format += '-'+tag_name
    time_format += '] '
    t = time.strftime( time_format, time.localtime( time.time() ) )
  else:
    if tag_name: t = '[' + tag_name + '] '
    else:   t = ''
  if tag_name:
    output( t + log_filter(str), tag(tag_name) )
  else:  
    output( t + log_filter(str) )
  
def update_output():
  global d, output_todo, setup
  mutex.acquire()
  if d:
    if output_todo != []:
      for t,l in output_todo:
        d.output.insert( END, l )
        if t:
          if t['tag'] in list(setup['tcolors'].keys()):
            i = d.output.index(END)
            start = d.output.index( i + ' - 2 lines')
            end = d.output.index( i + ' - 1 line')
            d.output.tag_add( t['tag'], start, end )
      try:
        if setup['scroll_mode']: d.output.see( END )
      except: pass
    output_todo = []  
  mutex.release()
  root.after(10, update_output)

update_output()


# -----------------------------------------------------------------------------
# - Thread to Run a Script (actually a Python Program...)
# -----------------------------------------------------------------------------
# Note: While the script program is running the script_name contains the
# filename! When the script is stopped by calling script_stop() the script
# name will be set to an empty string. Please make sure that the script
# does exit any loops it may contain when it detects that the script name
# is empty! Otherwise the user interface will be blocked trying to join a
# thread that doesn't end...
# It is not possible to run more than one script at the same time!

script_name = ''
script_th = None
script_data_handler = None

class ScriptThread( threading.Thread ):
  def run( self ):
    global d, script_name
    try:
      exec(compile(open( script_name, "rb" ).read(), script_name, 'exec'))
    except:
      output( '' )
      output( '>>> Exception raised in script <<<' )
      output( 'Traceback (most recent call last):' )
      for line in traceback.format_tb(sys.exc_info()[2]):
        output_str( line )
      output_str( sys.exc_info()[0] )  
      output_str( sys.exc_info()[1] )    
    script_name = ''
    print('ScriptThread done!')
    join_script_thread()

def script_autostart_set( filename=None ):
  global setup
  setup['autostart'] = filename

def script_run( filename=None ):
  global script_th, script_name, setup
  if script_th is None:
    if not filename:
      th_name = threading.currentThread().getName()
      if th_name == 'MainThread':
        filename = Open( setup_path_file_names=('script_path','script_file'),
                         filetypes=[('CommScript', '*.cs')],
                         title='Run a CommScript Script...' ).show()
        if filename:
          line = '=>script_run(\'' + filename + '\')'
          input_add( line )
          d.inputline.delete( 0, END )
          d.inputline.insert( END, line )
      else:
        print('ERROR: script_run() only allowed in main thread!')
    if filename:
      script_name = filename
      script_th = ScriptThread( name='ScriptThread' )
      update_button_run( 'Stop!' )
      script_th.start()
  else: print('Script already running?')

def script_edit( filename=None ):
  global script_th, script_name, setup
  if not filename:
    th_name = threading.currentThread().getName()
    if th_name == 'MainThread':
      filename = Open( setup_path_file_names=('script_path','script_file'),
                       filetypes=[('CommScript', '*.cs')],
                       title='Edit a CommScript Script...' ).show()
      if filename:
        line = '=>edit(\'' + filename + '\')'
        input_add( line )
        d.inputline.delete( 0, END )
        d.inputline.insert( END, line )
    else:
      print('ERROR: script_edit() only allowed in main thread!')
  if filename:
    edit( filename )

def script_stop():
  global script_th, script_name, script_dialog_active
  if script_name:
    if not script_dialog_active:
      script_name = '';
      if not (script_data_handler is None):
        #ensure that script may exit any waits...
        script_data_handler( '<<<STOP>>>' )
      #if script_th:
      #  script_th.join()
      #  script_th = None
      #update_button_run( 'Run...' )
    else:
      showerror('Operation Not Allowed!','The script still has a dialog box open and cannot be stopped. Please close the script\'s dialog box first!')
  else:
    if script_th:
      script_th.join()
      script_th = None


# -----------------------------------------------------------------------------
# - Thread to Catch and Handle RS-232 Data
# - Send Data to Port
# - Open and Close COM Port
# -----------------------------------------------------------------------------

class SerialInputThread( threading.Thread ):
  def run( self ):
    global tty, inbuffer, inlines, serial_mode, setup
    global script_name, script_th, script_data_handler
    flush_timeout = 0
    running = True
    while running:
      mutex.acquire()
      tty_ok = tty != None
      mutex.release()      
      if tty_ok:
        mutex.acquire()
        try:
            while (tty.inWaiting() > 0):
              flush_timeout = 0
              inbuffer = ENC(inbuffer)
              inbuffer += tty.read( tty.inWaiting() )
              if serial_mode in [ AT_CMD, USER_SPLIT ]:
                if serial_mode == AT_CMD:
                  lst = re.split( '\n', inbuffer )
                  def remove_r( ln ):
                    while ln and (ln[0]=='\r'): ln = ln[1:]
                    while ln and (ln[-1:]=='\r'): ln = ln[:-1]
                    return ln
                  inlines += list(map(remove_r,lst[:-1]))
                else:
                  if inbuffer:
                    lst = re.split( user_split_str, inbuffer )
                    inlines += lst[:-1]
                inbuffer = lst[-1]
                if d:
                  for line in inlines:
                    if line:
                      log_output( None, line )
                      if script_name and not (script_data_handler is None):
                        script_data_handler( line )
                inlines = []
        except:
            tty_ok = False
            tty = None
            log_output( 'ERR', "SERIAL PORT ERROR" )
            
        mutex.release()
        time.sleep( 0.1 )
        flush_timeout += 1
        if flush_timeout > 10:
          mutex.acquire()
          if inbuffer:
            if script_name and not (script_data_handler is None):
              script_data_handler( inbuffer )
            log_output( 'F', inbuffer )
            inbuffer = ''
          mutex.release()
          flush_timeout = 0
      else:
        running = False
    print('SerialInputThread done!')

def send( text: str ):
  if tty:
    bytes_to_write = bytes(text, encoding="latin_1", errors="ignore")
    tty.write( bytes_to_write )

def sendln( text: str ):
  global user_line_end
  send( text + user_line_end )

def sendhex( hexstr: str ):
  send( binascii.unhexlify( hexstr ) )

def comm_open( com_port, speed=115200, param='8N1', flow='None' ):
  global d, tty, s_th, setup
  tty = None
  try:
    if platform == PLATFORM_WIN:
      if len(com_port) > 4:
        tty = SerialPort( '\\\\.\\'+com_port, 1000, speed, 'rs232', param, flow )
      else:
        tty = SerialPort( com_port, 1000, speed, 'rs232', param, flow )
    if platform == PLATFORM_LINUX:
        tty = SerialPort( com_port, 1000, speed, 'rs232', param, flow )
    setup['port'] = com_port
    setup['speed'] = str(speed)
    setup['param'] = param
    setup['flowctrl'] = flow
  except:
    setup['ports'] = comm_checkports()
    d.dd_comport.update_menu( setup['ports'] )
    d.dd_comport.set( 0 )
    try:
      setup['port'] = setup['ports'][0]
    except KeyError:
      setup['ports'] = init_ports
      setup['port'] = init_ports[0]      
    print('Error')
  if tty:
    s_th = SerialInputThread( name='serial input thread' )
    s_th.start()

def comm_close():
  global d, tty, s_th, setup, script_th, script_name
  if tty:
    mutex.acquire()
    del tty
    tty = None
    mutex.release()
  if s_th:
    s_th.join()

def comm_checkports():
  result = []
  if platform == PLATFORM_WIN:
    for i in range(50):
      p = None
      try:
        if i > 9:
          p = SerialPort( '\\\\.\\COM'+str(i), 1000, 9600 )
        else:
          p = SerialPort( 'COM'+str(i), 1000, 9600 )
      except:
        pass
      if p:
        result += [ 'COM'+str(i) ]
        del p
  if platform == PLATFORM_LINUX:
    ports = glob.glob('/dev/tty[A-Za-z]*')
    for port in ports:
      p = None
      try:
        p = SerialPort( port, 1000, 9600 )
      except:
        pass
      if p:
        result += [ port ]
        del p
  return ['OFF'] + result

    
# -----------------------------------------------------------------------------
# Functions to Control the Input and Output Areas of the Dialog 
# -----------------------------------------------------------------------------

def scroll_auto():
  global setup
  setup['scroll_mode'] = True
  
def scroll_off():
  global setup
  setup['scroll_mode'] = False

def input_clear():
  if threading.currentThread().getName() == 'MainThread':
    d.input.delete( 0, END )

def input_add(line):
  if threading.currentThread().getName() == 'MainThread':
    if setup['ts_format']:
      tstr = time.strftime( '['+setup['ts_format']+'] ', time.localtime( time.time() ) )
    else: tstr = ''
    d.input.insert( END, tstr+line )
    try:
      if setup['scroll_mode']: d.input.see( END )
    except: pass

def input_load( filename=None, ignore_exception=False ):
  if threading.currentThread().getName() == 'MainThread':
    if not filename:
      filename = Open( setup_path_file_names=('in_path','in_file'),
                       filetypes=[('all files', '*')],
                       title='Open input history file...' ).show()
    if filename:
      try:
        infile = open( filename )
        input_clear()
        try:
          while 1:
            line = infile.readline()
            if not line: break
            while line[-1:] == '\r' or line[-1:] == '\n':
              line = line[:-1]
            d.input.insert( END, line )
        finally:
          infile.close()
      except:
        if not ignore_exception:
          output_str( '\n>>> Exception in input_load <<<' )
          output_str( sys.exc_info()[0] )  
          output_str( sys.exc_info()[1] )

def input_save( filename=None ):
  if threading.currentThread().getName() == 'MainThread':
    if not filename:
      filename = SaveAs( setup_path_file_names=('in_path','in_file'),
                         filetypes=[('all files', '*')],
                         title='Save input history file...' ).show()
    if filename:
      try:
        outfile = open( filename, 'w' )
        fields = d.input.get( 0, END )
        try:
          for eachfield in fields:
            outfile.write( eachfield + '\n' )
        finally:
          outfile.close()
      except:    
        output_str( '\n>>> Exception in input_save <<<' )
        output_str( sys.exc_info()[0] )  
        output_str( sys.exc_info()[1] )

def input_bind( event, callback ):
  if threading.currentThread().getName() == 'MainThread':
    d.input.bind( event, callback )

def output_bind( event, callback ):
  if threading.currentThread().getName() == 'MainThread':
    d.output.bind( event, callback )

def output_clear():
  if threading.currentThread().getName() == 'MainThread':
    d.output.delete( '1.0', END )

def output_load( filename=None, ignore_exception=False ):
  if threading.currentThread().getName() == 'MainThread':
    if not filename:
      filename = Open( setup_path_file_names=('out_path','out_file'),
                       filetypes=[('all files', '*')],
                       title='Open output log file...' ).show()
    if filename:
      try:
        infile = open( filename, 'r' )
        output_clear()
        try: d.output.insert( END, infile.read() )
        finally: infile.close()
      except:
        if not ignore_exception:
          output_str( '\n>>> Exception in output_load <<<' )
          output_str( sys.exc_info()[0] )
          output_str( sys.exc_info()[1] )
      try:
        with open(filename+'.tags.json') as fp:
          t_dict = json.load(fp)
        if type( t_dict ) == type( {} ):
          c = t_dict['tag_info']
          for k in list(c.keys()):
            (setup['tcolors'])[k] = c[k]
          t_dict.pop('tag_info')
          tag_reconfigure()
          set_tags( t_dict )
      except: pass

def output_save( filename=None ):
  if threading.currentThread().getName() == 'MainThread':
    if not filename:
      filename = SaveAs( setup_path_file_names=('out_path','out_file'),
                         filetypes=[('all files', '*')],
                         title='Save output log file...' ).show()
    if filename:
      try:
        outfile = open( filename, 'w' )
        try:
          out_str = d.output.get('1.0', END)
          outfile.write(out_str[:-1])         #20210724 - without this, the outputfile grew 1 empty line at the end after load-save-load...
        finally: outfile.close()
      except:
        output_str( '\n>>> Exception in output_save <<<' )
        output_str( sys.exc_info()[0] )
        output_str( sys.exc_info()[1] )
      t_dict = get_tags()
      save_tags = []
      for k in list(t_dict.keys()):
        if t_dict[k]: save_tags += [ k ]
      if save_tags:
        global setup
        c = setup['tcolors']
        used_colors_dict = {}
        for t in save_tags:
          try: used_colors_dict[t] = c[t]
          except KeyError: pass
        t_dict['tag_info'] = used_colors_dict
        with open(filename+'.tags.json', 'w') as fp:
          json.dump(t_dict, fp)

def output_bind( event, callback ):
  if threading.currentThread().getName() == 'MainThread':
    d.output.bind( event, callback )

def output_curpos_set( x, y ):
  if threading.currentThread().getName() == 'MainThread':
    d.output.mark_set( 'insert', str(y)+'.'+str(x) )

def output_curpos_get():
  if threading.currentThread().getName() == 'MainThread':
    y, x = re.split( '\.', d.output.index( 'insert' ) )
    return int(x), int(y)
  else: return None

def output_text_get( x1, y1, x2, y2 ):
  if threading.currentThread().getName() == 'MainThread':
    return d.output.get( str(y1)+'.'+str(x1), str(y2)+'.'+str(x2) )
  else: return None

def output_curline_get():
  if threading.currentThread().getName() == 'MainThread':
    x, y = output_curpos_get()
    return output_text_get( 0, y, 0, y+1 )[:-1]
  else: return None

def output_line_get( y ):
  if threading.currentThread().getName() == 'MainThread':
    return output_text_get( 0, y, 0, y+1 )[:-1]
  else: return None

def inputline_set( text=None ):
  if threading.currentThread().getName() == 'MainThread':
    d.inputline.delete( 0, END )
    if text:
      d.inputline.insert( END, text )
    
def inputline_get():
  if threading.currentThread().getName() == 'MainThread':
    return d.inputline.get()
  else: return None 

def inputline_bind( event, callback ):
  if threading.currentThread().getName() == 'MainThread':
    d.inputline.bind( event, callback )

def save():
  if threading.currentThread().getName() == 'MainThread':
    d.save_event( None )


# -----------------------------------------------------------------------------
# Main Window
# -----------------------------------------------------------------------------

class MyDialog:

  clear_OK = False;
    
  def __init__( self, master, title=None ):
    global sv_status, sv_comma, setup
    self.autosave_job = None
    self.autosave_var = IntVar()
    self.autosave_var.set(1)
    self.search_results = []
    self.search_tag_last_result_highlight = 0
    self.search_tag_last_char_searched = 0    
    self.last_search = None
    setup['ports'] = comm_checkports()
    if title is None: 
      try:
        title = setup['title']
      except:
        title = 'Terminal Window'
    self.master = master
    self.directory = None
    self.top = Toplevel( master )
    self.top.title( title )
    self.top.iconname( title )
    if setup['geometry']:  
      self.top.geometry( setup['geometry'] )
    self.bottomframe = Frame( self.top )
    self.bottomframe.pack( side=BOTTOM, fill=X )
    self.sv_comport = StringVar()
    self.sv_comport.trace( 'w', self.change_port_settings )
    try:
      outputFont = setup['outputFont']
    except KeyError:
      setup['outputFont'] = init_outputFont
      outputFont = init_outputFont
    try:
      outputWidth = setup['outputWidth']
    except KeyError:
      setup['outputWidth'] = init_outputWidth
      outputWidth = init_outputWidth
    try:
      outputHeight = setup['outputHeight']
    except KeyError:
      setup['outputHeight'] = init_outputHeight
      outputHeight = init_outputHeight
    try:
      inputFont = setup['inputFont']
    except KeyError:
      setup['inputFont'] = init_inputFont
      inputFont = init_inputFont
    try:
      inputWidth = setup['inputWidth']
    except KeyError:
      setup['inputWidth'] = init_inputWidth
      inputWidth = init_inputWidth
    try:
      inputlineFont = setup['inputlineFont']
    except KeyError:
      setup['inputlineFont'] = init_inputlineFont
      inputlineFont = init_inputlineFont
    try:
      inputlineWidth = setup['inputlineWidth']
    except KeyError:
      setup['inputlineWidth'] = init_inputlineWidth
      inputlineWidth = init_inputlineWidth
    try:
      port_choices = setup['ports']
    except KeyError:
      setup['ports'] = init_ports
      port_choices = init_ports
    self.dd_comport = DropDown( self.bottomframe, self.sv_comport, port_choices )
    self.dd_comport.pack( side=LEFT )    
    self.sv_speed = StringVar()
    self.sv_speed.trace( 'w', self.change_port_settings )
    try:
      speed_choices = setup['speeds']
    except KeyError:
      setup['speeds'] = init_speeds
      speed_choices = init_speeds
    self.dd_speed = DropDown( self.bottomframe, self.sv_speed, speed_choices )
    self.dd_speed.pack( side=LEFT )
    self.sv_param = StringVar()
    self.sv_param.trace( 'w', self.change_port_settings )
    try:
      param_choices = setup['params']
    except KeyError:
      setup['params'] = init_params
      param_choices = init_params
    self.dd_param = DropDown( self.bottomframe, self.sv_param, param_choices )
    self.dd_param.pack( side=LEFT )
    self.sv_flowctrl = StringVar()
    self.sv_flowctrl.trace( 'w', self.change_port_settings )
    try:
      flowctrl_choices = setup['flowctrls']
    except KeyError:
      setup['flowctrls'] = init_flowctrls
      flowctrl_choices = init_flowctrls
    self.dd_flowctrl = DropDown( self.bottomframe, self.sv_flowctrl, flowctrl_choices )
    self.dd_flowctrl.pack( side=LEFT )
    try:
      self.dd_comport.set( setup['ports'].index( setup['port'] ) )
    except:
      self.dd_comport.set( 0 )
    try:
      self.dd_speed.set( setup['speeds'].index( setup['speed'] ) )
    except:
      self.dd_speed.set( 0 )
    try:
      self.dd_param.set( setup['params'].index( setup['param'] ) )
    except:
      self.dd_param.set( 0 )
    try:
      self.dd_flowctrl.set( setup['flowctrls'].index( setup['flowctrl'] ) )
    except:
      self.dd_flowctrl.set( 0 )
    def button_edit_handler( s=self ):
      script_edit()
    self.button_edit = Button( self.bottomframe, text='Edit...', command=button_edit_handler )
    self.button_edit.pack( side=LEFT, fill=Y )
    def button_run_handler( s=self ):
      global script_name
      if script_name: script_stop()
      else: script_run()
    self.button_run = Button( self.bottomframe, text='Run...', command=button_run_handler )
    self.button_run.pack( side=LEFT, fill=Y )
    self.label_status = Label( self.bottomframe, textvariable=sv_status )
    self.label_status.pack( side=LEFT )
    update_status_line( version.version )
    self.bar = ProgressBarView( self.bottomframe, value=0 )
    self.bar.pack( side=RIGHT, fill=X )
    self.inputline = Entry( self.top, width=inputlineWidth, font=inputlineFont )
    self.inputline.pack( side=BOTTOM, fill=X )
    self.inputline.bind( '<Return>', self.ok_event )
    self.inputline.bind( '<Up>', self.up_event )
    self.inputline.bind( '<Down>', self.down_event )
    self.inputline.bind( '<Left>', self.left_event )
    self.inputline.bind( '<Right>', self.right_event )
    self.inputline.bind( '<Home>', self.home_event )
    self.inputline.bind( '<End>', self.end_event )
    self.inputline.bind( '<Scroll_Lock>', self.scroll_lock_event )
    self.inputline.bind( '<Escape>', self.esc_event )
    self.inputline.bind( '<F11>', self.f11_event )
    self.inputline.bind( '<F12>', self.f12_event )
    self.inputline.bind( '<Control-s>', self.save_event )
    self.inputline.bind( '<Control-S>', self.save_event )
    self.midframe = Frame( self.top )
    self.midframe.pack( expand=YES, fill=BOTH )
    self.output = None
    self.addoptions()
    self.compiled = None
    self.recompile()
    self.outputbar = Scrollbar( self.midframe )
    self.outputbar.pack( side=RIGHT, fill=Y )
    self.output = Text( self.midframe, exportselection=0, width=outputWidth, height=outputHeight, \
      yscrollcommand=(self.outputbar,'set'), font=outputFont )
    self.output.pack( side=RIGHT, expand=YES, fill=BOTH )
    self.outputbar.config( command=(self.output,'yview') )
    self.output.bind( '<Control-s>', self.save_event )
    self.output.bind( '<Control-S>', self.save_event )
    self.output.bind( '<F2>', self.f2_event )
    self.output.bind( '<F3>', self.f3_event )
    self.output.bind( '<Escape>', self.esc_in_output_event )
    self.output.bind( '<Scroll_Lock>', self.scroll_lock_event )

    output_menu = Menu( self.output, tearoff=0 )
    fun_lst = [ ('Delete All',output_clear),('Save As...',output_save),('Load From...',output_load) ]
    for n,f in fun_lst:
      output_menu.add_command( label=n, command=f )
    output_sel_atag_menu = Menu( self.output, tearoff=0 )
    allTags = list(setup['tcolors'].keys())
    selTag = StringVar()
    selTag.set(list(allTags)[0])
    def chgSelTag():
      try:
        start, end = self.output.tag_ranges( 'sel' )
        self.output.tag_add( selTag.get(), start, end )
      except: pass  
    for t in allTags:
      output_sel_atag_menu.add_radiobutton( label=t, variable=selTag, command=chgSelTag )
    def rmSelTags():
      try:
        start, end = self.output.tag_ranges( 'sel' )
        for t in list(setup['tcolors'].keys()):
          if t != 'sel':
            self.output.tag_remove( t, start, end )
      except: pass  
    output_sel_menu = Menu( self.output, tearoff=0 )
    output_sel_menu.add_cascade( label='Apply Tag', menu=output_sel_atag_menu )
    output_sel_menu.add_command( label='Remove Tags', command=rmSelTags )
    output_menu.add_cascade( label='Selection', menu=output_sel_menu )
    def output_popUpMenu( event ):
      output_menu.post( event.x_root, event.y_root )
    self.output.bind( '<Button-3>', output_popUpMenu )

    self.inputbar = Scrollbar( self.midframe )
    self.inputbar.pack( side=LEFT, fill=Y )
    self.input = Listbox( self.midframe, selectmode=SINGLE, \
      exportselection=0, width=inputWidth, yscrollcommand=(self.inputbar,'set'), font=inputFont )
    self.input.pack( side=LEFT, expand=NO, fill=BOTH )
    self.inputbar.config( command=(self.input,'yview') )
    btags = self.input.bindtags()
    self.input.bindtags( btags[1:] + btags[:1] )
    self.inputline.bind( '<KeyPress>', self.keypress )
    self.inputline.bind( '<KeyRelease>', self.recompile )
    self.inputline.bind( '<ButtonRelease-1>', self.inputline_select_event )
    self.input.bind( '<ButtonRelease-1>', self.input_select_event )
    self.input.bind( '<Double-ButtonRelease-1>', self.input_double_event )
    self.input.bind( '<Control-s>', self.save_event )
    self.input.bind( '<Control-S>', self.save_event )
    self.top.protocol( 'WM_DELETE_WINDOW', self.quit )

  def addoptions(self):
    self.frames = []
    self.boxes = []
    self.vars = []
    frame = Frame( self.top )
    frame.pack( fill=X )
    self.frames.append( frame )
  
    box = Checkbutton( frame, variable=self.autosave_var, text='Auto-Save', offvalue=0, onvalue=1,
                       command=self.change_autosave )
    box.pack( side=RIGHT )
    self.boxes.append( box )
    
    self.promptdisplay = Label( frame, anchor=W,
                                text='Start with // for regular expression. Options:' )
    self.promptdisplay.pack( side=LEFT )
    for name in ( 'ASCII', 'IGNORECASE', 'VERBOSE' ):
      val = 're.' + name
      var = StringVar()
      var.set('0')
      box = Checkbutton( frame, variable=var, text=name, offvalue='0', onvalue=val,
                         command=self.recompile )
      box.pack( side=LEFT )
      self.boxes.append( box )
      self.vars.append( var )
    self.statusdisplay = Label( frame, text='' )
    self.statusdisplay.pack( side=LEFT, fill=X )

  def getflags(self):
    flags = ''
    for var in self.vars:
      flags = flags + var.get() + '|'
    if flags != '':
      flags = flags[:-1]
    return eval(flags)

  def keypress(self, event=None):
    if event.char != '':
      if event.char == chr(8):
        self.clear_OK = False           
      elif self.clear_OK:
        self.inputline.delete( 0, END )
        self.clear_OK = False

  def autosave(self):
    save()
    self.autosave_job = root.after( 60*1000, self.autosave )

  def change_autosave(self, event=None):
    if self.autosave_var.get():
      self.autosave()
    else: # cancel autosave      
      if self.autosave_job is not None:
        root.after_cancel(self.autosave_job)
        self.autosave_job = None

  def recompile(self, event=None):
    e = None
    line = self.inputline.get()
    if line[:2] == '//':
      self.last_search = line
      e = line[2:]
    if e:
      try:
        self.compiled = re.compile( e, self.getflags() )
        bg = self.promptdisplay['background']
        self.statusdisplay.config( text="", background=bg )
      except re.error as msg:
        self.compiled = None
        self.statusdisplay.config( text="  re.error: %s  " % str(msg), background="red" )
      self.removetags()
      nmatches = self.reevaluate(0)
      
      if nmatches > 0:
        self.output.see( tk_get_index_from_position(self.search_results[0][0]) )

      if nmatches == 0:
        self.statusdisplay.config( text="  (no match)  ", background="yellow" )
      else:
        self.statusdisplay.config( text="" )
      
    elif line[:2] == '//': self.removetags()

  def removetags(self):
    self.search_results = []
    self.search_tag_last_result_highlight = 0
    self.search_tag_last_char_searched = 0
    if not self.output: return
    try: self.output.tag_remove( "hit", "1.0", END )
    except TclError: pass
    try: self.output.tag_remove( "hit0", "1.0", END )
    except TclError: pass

  def reevaluate(self, initial_char = 0, timeout_secs = 10.0, event=None):
    if not self.compiled:
      return

    self.search_tag_last_char_searched = self.output.count('1.0','end','chars')[0]
    text = self.output.get( tk_get_index_from_position(initial_char), tk_get_index_from_position(self.search_tag_last_char_searched) )
    
    last = 0
    nmatches = 0
    
    time_start = time.time()
    timeout = False
    
    while last <= len( text ) and not timeout:
      m = self.compiled.search( text, last )
      if m is None:
        break
      first, last = m.span()
      if last == first:
        last = first + 1

      self.search_results += [ (first + initial_char, last + initial_char) ]
      nmatches = nmatches + 1
      timeout = (time.time() - time_start) > timeout_secs

    if timeout:
        self.search_tag_last_char_searched = last
      
    return nmatches

  def go( self ):
    self.inputline.focus_set()
    self.top.wait_visibility()      # window needs to be visible for the grab
    self.how = None
    input_load( setup['startup_path']+'/input.txt', True )
    output_load( setup['startup_path']+'/output.txt', True )
    self.flist = my_idlelib.filelist.FileList(self.master)
    if setup['autostart']:
      script_run( setup['autostart'] )
    self.master.mainloop()          # Exited by self.quit(how)
    self.top.destroy()
    return 0

  def quit( self, how=None ):
    global script_name
    if self.flist.dict == {}:
      if script_name: script_stop()
      if not script_name:
        self.how = how
        setup['geometry'] = self.top.geometry();
        input_save( setup['startup_path']+'/input.txt' )
        output_save( setup['startup_path']+'/output.txt' )    
        self.master.quit()              # Exit mainloop()
    else:
      showerror('Operation not allowed','Please close all Edit windows before exiting...')

  def update_inputbox( self ):
    line = self.input.get( 'active' )
    if line:
      if line[0] == '[':
        while line and line[0]!=']': line = line[1:]
        while line and line[0]==']': line = line[1:]        
        while line and line[0]==' ': line = line[1:]  
      self.inputline.delete( 0, END )
      self.inputline.insert( END, line )
      self.inputline.focus_set()

  def scroll_lock_event( self, event ):
    global setup
    try: setup['scroll_mode'] = not setup['scroll_mode']
    except: setup['scroll_mode'] = True

  def esc_event( self, event ):
    line = self.inputline.get()
    if line[:2] == '//':
      self.output.see( 'insert' )
      self.output.focus_set()
    else:
      self.input.select_clear( 0, END )

  def esc_in_output_event( self, event ):
    self.inputline.focus_set()

  def f2_event( self, event ):
    if self.last_search:
      inputline_set( self.last_search )
      # self.recompile()
    if self.search_results:
      cursor_pos = self.output.index( 'insert' )

      last_pos = tk_get_index_from_position(self.search_results[-1][0])
      
      for search_pos in self.search_results:
        if self.output.compare( tk_get_index_from_position(search_pos[0]), '>=', cursor_pos ):
          self.output.mark_set( 'insert', last_pos )
          self.output.see( 'insert' )
          return
        else: last_pos = tk_get_index_from_position(search_pos[0])
      self.output.mark_set( 'insert', last_pos )
      self.output.see( 'insert' )
  
  def f3_event( self, event ):
    if self.last_search:
      inputline_set( self.last_search )
      # self.recompile()
    if self.search_results:
      cursor_pos = self.output.index( 'insert' )
      for search_pos in self.search_results:
        if self.output.compare( tk_get_index_from_position(search_pos[0]), '>', cursor_pos ):
          self.output.mark_set( 'insert', tk_get_index_from_position(search_pos[0]) )
          self.output.see( 'insert' )
          return
      self.output.mark_set( 'insert', tk_get_index_from_position(self.search_results[0][0]) )
      self.output.see( 'insert' )

  def f11_event( self, event ):
    csel = self.input.curselection()
    if csel: 
      cline = int ( csel[0] )
      self.input.delete( cline )
      if cline < self.input.size():
        self.input.select_set( cline )
        self.input.activate( cline )
        self.update_inputbox()

  def f12_event( self, event ):
    self.inputline.delete( 0, END )

  def exec_inputline( self ):
    line = self.inputline.get()
    input_add( line )
    if line[:2] == '=>':
      try:
        exec( line[2:] )
      except:
        output( '' )
        output( '>>> Exception in exec from inputline <<<' )
        output_str( sys.exc_info()[0] )  
        output_str( sys.exc_info()[1] )    
    elif line[:2] == '=?':
      try:
        log_output( 'eval', repr (eval( line[2:] )) )
      except:
        output( '' )
        output( '>>> Exception in eval from inputline <<<' )
        output_str( sys.exc_info()[0] )  
        output_str( sys.exc_info()[1] )    
    elif line[:2] == '=#':
      sendhex( line[2:] )
    elif line[:2] == '=$':
      send( eval( '"\'' + line[2:] + '\'"' )[1:-1] )
    elif line[:2] == '//':
      if self.search_results:
        self.output.mark_set( "insert", tk_get_index_from_position(self.search_results[0][0]) )
      else:  
        self.output.mark_set( "insert", END )
      self.output.see( "insert" )
      self.output.focus_set()
    elif line[:2] == '\\\\':
      # Execute script, e.g '\\rtf' should run rtf.cs from the scripts folder
      global script_th, script_name
      if script_th is None and not script_name:
        lst = re.split( ' ', line[2:] )
        scriptFile = 'scripts/' + lst[0] + '.cs'
        output_str(scriptFile)
        try:
          if len(lst) > 1:
            exec("global PARAMS; PARAMS='"+line[line.find(' ')+1:]+"'")
        except:
          output( '' )
          output( '>>> Exception in PARAMS for \\<script> PARAMS from inputline <<<' )
          output_str( sys.exc_info()[0] )  
          output_str( sys.exc_info()[1] )    
        script_run(scriptFile)
      else:
        output( '>>> is a script already running? <<<' )       
    else:
      sendln( line )

  def ok_event( self, event ):
    self.exec_inputline()
    if self.bar.value == 100:
      update_progress( 0 )
      update_status_line( version.version )
    if event.char == chr(13):
      self.clear_OK = True

  def up_event( self, event ):
    self.clear_OK = False
    csel = self.input.curselection()
    cline = END;
    if csel: cline = int ( csel[0] )
    self.input.select_clear( 0, END )
    if cline > 0 and cline != END: cline -= 1
    self.input.select_set( cline )
    self.input.activate( cline )
    self.update_inputbox()
    try:
      if setup['scroll_mode']: self.input.see( ACTIVE )
    except: pass

  def down_event( self, event ):
    self.clear_OK = False    
    csel = self.input.curselection()
    cline = END;
    if csel: cline = int ( csel[0] )
    self.input.select_clear( 0, END )
    if cline < self.input.size()-1 and cline != END: cline += 1
    self.input.select_set( cline )
    self.input.activate( cline )
    self.update_inputbox()
    try:
      if setup['scroll_mode']: self.input.see( ACTIVE )
    except: pass

  def left_event( self, event ):
    self.clear_OK = False    

  def right_event( self, event ):
    self.clear_OK = False    

  def home_event( self, event ):
    self.clear_OK = False    

  def end_event( self, event ):
    self.clear_OK = False    

  def input_double_event( self, event ):
    self.clear_OK = True
    self.update_inputbox()
    self.exec_inputline()
    self.recompile()
    
  def input_select_event( self, event ):
    self.clear_OK = False
    self.update_inputbox()
    self.recompile()

  def inputline_select_event( self, event ):
    self.clear_OK = False

  def change_port_settings( self, *args ):
    port = self.sv_comport.get()
    speed = self.sv_speed.get()
    param = self.sv_param.get()
    flow = self.sv_flowctrl.get()
    if port and speed and param and flow:
      comm_close()
      #print port, speed, param, flow
      if port != 'OFF':
        comm_open( port, int(speed), param, flow )
      else:
        setup['port'] = 'OFF'
        setup['speed'] = speed
        setup['param'] = param        
        setup['flowctrl'] = flow        
        setup['ports'] = comm_checkports()
        self.dd_comport.update_menu( setup['ports'] )
        self.dd_comport.set(0)

  def save_event( self, event ):
    output_save( setup['startup_path']+'/output.txt' )    
    input_save( setup['startup_path']+'/input.txt' )
    with open(setup['startup_path']+'/setup.json', 'w') as fp:
      json.dump(setup, fp)
    
# -----------------------------------------------------------------------------
# Program Start Right Here...
# -----------------------------------------------------------------------------

def run_main():
    global root, d, du, sv_status, setup
    try:
      with open('setup.json') as fp:
        data = json.load(fp)
        setup.update(data)
    except:
      pass
    setup['startup_path'] = os.getcwd()
    tag_reconfigure()
    root.withdraw()
    sv_status = StringVar()
    if len(sys.argv) >= 2:
      if sys.argv[1] == '/install':
        if not askyesno('Congratulations!', 'CommScript is now installed!\n\nRun CommScript now?'):
          sys.exit()
    d = MyDialog( root )
    root.after(1000, cooperative_multitasking_please_kill_the_tk_creator_in_the_past)
    d.change_autosave()
    
    r = d.go()
    with open(setup['startup_path']+'/setup.json', 'w') as fp:
      json.dump(setup, fp)
    comm_close()
    if script_th:
      script_stop()

def cooperative_multitasking_please_kill_the_tk_creator_in_the_past():
    global root, d
    
    current_char = d.output.count('1.0','end','chars')[0]
    
    if d.search_tag_last_char_searched < current_char:
        # Search in new text
        d.reevaluate(d.search_tag_last_char_searched, 0.02)
        
    if d.search_tag_last_result_highlight < len(d.search_results):
        # Highlight 
        time_start = time.time()
        timeout_secs = 0.04
        timeout = False
        
        while d.search_tag_last_result_highlight < len(d.search_results) and not timeout:
            d.output.tag_add( 'hit', 
                             tk_get_index_from_position(d.search_results[d.search_tag_last_result_highlight][0]), 
                             tk_get_index_from_position(d.search_results[d.search_tag_last_result_highlight][1]))
            d.search_tag_last_result_highlight += 1
            timeout = (time.time() - time_start) > timeout_secs

    root.after(100, cooperative_multitasking_please_kill_the_tk_creator_in_the_past)
    

if __name__ == '__main__':
    run_main()
