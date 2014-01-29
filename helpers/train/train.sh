#! /bin/bash

#train.sh
#automated sample recording for sphinxtrain

BASENAME=$1
RANGESTART=$2
RANGEEND=$3

if [[ (-z $1) || (-z $2) || (-z $3)]]; then
	echo "parameter error"
	echo "use \"train filename startrange endrange\""
	exit 1
fi


for I in `seq $2 $3`;
do
	aplay beep-02.wav
	echo "$BASENAME$I.wav"
	sleep 0.3
	arecord -r 16000 -D hw:1,0 -d 5 -f S16_LE -c 1 $BASENAME$I.wav
done

