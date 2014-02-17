#! /bin/bash
#checks if there to low closed ports, perhaps, while sip client is running
#per deafult there should be only port 22 and evtl. 8888 open

DEFAULT_CLOSED_PORTS=65533
CLOSED_PORTS=`nmap -p- 192.168.10.158 | grep "Not shown" | cut -d ' ' -f3`

if [ $CLOSED_PORTS -lt $DEFAULT_CLOSED_PORTS ]
then
	aplay /home/falko/development/seheiah/audiofiles/beep-02.wav
fi
exit 0
