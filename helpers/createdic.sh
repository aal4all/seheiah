#! /bin/bash
# creates phonetic dictionary for seheiah based on vocabulary and pronouncation lexicon

while read word;
do
	dic=`egrep -i -e ^$word ~/seheiah/Lexicon/voxDE20090209.pr0n`
	echo "#$word" >> seheiah_de.vocab.dic
	echo $dic >> seheiah_de.vocab.dic
done < seheiah_de.vocab

