# check-seheiahd-status.sh
# checks, if seheiahd is running
# you shuould run it in cronjob
#!/bin/bash
if [ `ps -e | grep -c "seheiah" ` -eq 0 ]
then
	PATH_TO_SEHEIAH="/home/falko/seheiah"
  echo "Daemon ist gestorben" | /usr/bin/mail -s "Daemon ist tot" mail@address
  mpg321 -o alsa -a hw:0,0 $PATH_TO_SEHEIAH/audiofiles/de_seheiahd_isnt_running.mp3
  cd $PATH_TO_SEHEIAH/program
  ./seheiahd.py start
fi
echo $?

