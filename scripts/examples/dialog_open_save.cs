
# this script shows how to use filename input dialogs...
# the first parameter is used to define a name for path and file to be
# stored in the global setup when the terminal window is closed. 
# The last values of the dialog box will be remembered until the script
# is run again (if the names are unique - if the same name is used in
# an other script or is a name of the main program the last remembered
# setting for this name will be restored)
# Please note that the following names are used by the main program:
#   dwl_path, dwl_file, in_path, in_file, out_path, out_file,
#   script_path, script_file
# You may wish to use those on purpose for example the dwl* ones to get
# access to the saved setting of the "X" (XModem send) button of the GUI


output_str( '\n\nFILE DIALOG TEST...\nPlease choose filenames in the dialog boxes!' )

fname = dialog_open( ('my_path1','my_file1'), 'Open A File...', [('all files', '*.*')] )
output( '1) Open: Filename:', fname )

fname = dialog_saveas( ('my_path2','my_file2'), 'SaveAs...', [('text files', '*.txt')] )
output( '2) SaveAs: Filename:', fname )

output_str( 'TEST FINISHED!\n' )
