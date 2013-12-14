# check-pulseaudio-status.sh
# checks, if pulseaudio is running and starts the service, when it isn't
# you should run it in a cronjob
#!/bin/bash
SERVICE='pulseaudio'
if  [ `ps -e | grep -c $SERVICE ` -eq 0 ]
then
	PATH_TO_SEHEIAH="/home/falko/seheiah"
	mpg321 -o alsa -a hw:0,0 $PATH_TO_SEHEIAH/audiofiles/de_pulseaudio_isnt_running.mp3
	sleep 3
  dbus-launch --exit-with-session pulseaudio --daemon
else
  echo "$SERVICE service running, everything is fine"
fi
exit $?
