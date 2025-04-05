# start.sh
#!/bin/sh
python emailapp.py &
python app.py &
wait