# check-seheiahd-status.sh
# checks, if seheiahd is running
# you shuould run it in cronjob
#!/bin/bash
if [ `ps -e | grep -c "seheiahd.py" ` -eq 0 ]
then
	echo "Daemon ist gestorben" | /usr/bin/mail -s "Daemon ist tot" mail@address
	sleep 10
	PATH_TO_SEHEIAH="/home/falko/seheiah"
	mpg321 -o alsa -a hw:0,0 $PATH_TO_SEHEIAH/audiofiles/de_seheiahd_isnt_running.mp3
	
  #starts seheiah in screen session, otherwise it doesn't works in cronjob
	if [ `screen -ls | grep -c "screen-seheiah" ` -eq 0 ]
	then
		#create screen session, workaraound to send command to session
    #see http://stackoverflow.com/questions/4440633/
    screen -dmS spawner bash -c "sleep 60"
    screen -S spawner -X screen screen -dR screen-seheiah -t screen-seheiah
    sleep 2
    screen -S screen-seheiah -p screen-seheiah -X detach
    screen -S screen-seheiah -p screen-seheiah -X stuff "/home/falko/seheiah/helpers/start-seheiahd.sh
    "
	else
		#Reattach a session and if necessary detach it first.
		screen -S screen-seheiah -p screen-seheiah -X detach
    screen -S screen-seheiah -p screen-seheiah -X stuff "/home/falko/seheiah/helpers/start-seheiahd.sh
    "	
	fi
fi
echo $?

/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games
