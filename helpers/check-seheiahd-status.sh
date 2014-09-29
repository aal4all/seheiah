# check-seheiahd-status.sh
# checks, if seheiahd is running
# you shuould run it in cronjob
#!/bin/bash

PATH_TO_SEHEIAH="/home/falko/seheiah"

if [ `ps -e | grep -c "seheiahd.py"` -eq 0 ]
then
	echo "Daemon ist gestorben" | /usr/bin/mail -s "Daemon ist tot" f.benthin@jpberlin.de
	sleep 10
	mpg321 -o alsa -a hw:0,0 $PATH_TO_SEHEIAH/audiofiles/de_seheiahd_isnt_running.mp3
	cd $PATH_TO_SEHEIAH/program/
	sudo ./seheiahd.py start
fi

if [ `ps -e | grep -c "seheiahd.py"` -eq 0 ]
then
        echo "PocketSphinx ist gestorben" | /usr/bin/mail -s "Daemon ist tot" f.benthin@jpberlin.de
        sleep 10
        mpg321 -o alsa -a hw:0,0 $PATH_TO_SEHEIAH/audiofiles/de_seheiahd_isnt_running.mp3
        cd $PATH_TO_SEHEIAH/program/
        ./gstSphinxCli.py 
fi

exit 0
