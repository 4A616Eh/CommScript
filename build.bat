
del /F /S /Q build dist
rmdir /S /Q build dist
pyinstaller commscr.spec
git show --format=reference >dist\git-ref.txt
python tools\create-zip.py
pause
