# lang_saver
Save language per window 


# installation and run
pip install -r requirements.txt
./lang_saver.py &

# i3-wm
echo 'exec --no-startup-id ~/bin/lang_saver.py &' >> ~/.config/i3/config

