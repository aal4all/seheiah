# check-internet-connection.sh
# checks internet connection
# you can insert / add your own urls and change the threshold
# you should run it in a cronjob
#! /bin/bash
URLS=('www.kernel.org' 'www.debian.org' 'www.archlinux.org');
COUNT=0
for (( i=0; i<${#URLS[@]}; i++ ))
do
	ping -W2 -c1 ${URLS[$i]} > /dev/null
	if [ "$?" -eq 0 ]
	then
		let "COUNT += 1"
		echo $COUNT
	fi
done
if [ $COUNT -eq 0 ]
then
	PATH_TO_SEHEIAH="/home/falko/seheiah"
	mpg321 -o alsa -a hw:0,0 $PATH_TO_SEHEIAH/audiofiles/de_lost_internet_connection.mp3
fi
