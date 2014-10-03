#starts seheiah daemon and speech recognition

#! /bin/bash

case $1 in

start)
	cd ~/seheiah/program
	echo "check if file seheiah_absence exists"
	#get name of absence file and path to seheiah
	ABSENCEFILE=`awk -F\= '$1 == "absenceFile " {sub(/^\ /, "", $2); print $2}' seheiah.cfg`
	DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
	ABSENCEFILE="$DIR/$ABSENCEFILE"
	echo $ABSENCEFILE
	if [ ! -f $ABSENCEFILE ]
	then
		echo "file doesn't exists ..."
		echo 0 > $ABSENCEFILE
		echo "... created"
	fi
	echo "start seheiahd (Monitor) ..."
	sudo ./seheiahd.py start
	sleep 10
	echo "done"
	
	echo "start speech recognition ..."
	./gstSphinxCli.py
	echo "done"
	;;

stop)

	cd ~/seheiah/program
	echo "check if file seheiah_absence exists"
        #get name of absence file and path to seheiah
        ABSENCEFILE=`awk -F\= '$1 == "absenceFile " {sub(/^\ /, "", $2); print $2}' seheiah.cfg`
        DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
        ABSENCEFILE="$DIR/$ABSENCEFILE"
	rm $ABSENCEFILE 
	echo "$ABSENCEFILE deleted"
	echo "stop pocketsphinx ..."
	killall gstSphinxCli.py
	echo "... done"
	echo "stop seheiahd ..."
	sudo ./seheiahd.py stop
	echo "... done"
	;;

*)
	echo "use ./seheiah_control.sh start|stop"
	;;
	
esac
exit 0
