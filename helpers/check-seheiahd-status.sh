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
	
	#check for pigpiod
	#if pir activated
	if [ `grep -c "pir = true" $PATH_TO_SEHEIAH/program/seheiah.cfg` -eq 1 ]
	then
		#check if prog exists
		if [ -f /usr/local/bin/pigpiod ]
		then
			#and start it if isn't running
			if [ `ps -e | grep -c "pigpiod" ` -eq 0 ]
			then
				sudo pigpiod
			fi
		else
			echo "ERROR: install pigpiod" | tee $PATH_TO_SEHEIAH/logs/seheiah.log
			exit 1
		fi
	fi
	
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

