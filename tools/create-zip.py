
import os
import sys
cwd = os.getcwd()
print(cwd)
sys.path.append(cwd)
import version
import string
from zipfile import ZipFile

v = version.version[-4:]
version_number = ''
if (v[0] in string.digits) and (v[1]=='.') and (v[2] in string.digits) and (v[3] in string.digits):
    version_number = v.replace('.','_') + '_'

dir = os.getcwd()

githash = 'XXXXXXX'

lines = []
with open(dir+'\\dist\\git-ref.txt','r') as f:
    for line in f:
        lines.append(line)
    line = lines[0]
    githash = line.split()[0]

filename = 'commscr_' + version_number + githash + '.zip'

def zipdir(path, handle):
    for root, dirs, files in os.walk(path):
        for file in files:
            handle.write( os.path.join(root, file),
                os.path.relpath(os.path.join(root, file), os.path.join(path,'..')) )

file = ZipFile(dir+'\\dist\\'+filename, 'w')
zipdir('dist/commscr', file)
file.close()
