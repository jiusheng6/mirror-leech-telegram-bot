source mltbenv/bin/activate
nohup ./alist server &
python3 update.py && python3 -m bot
