# starts seheiah daemon
#!/bin/bash
. ~/profile
PATH_TO_SEHEIAH="/home/falko/seheiah"
cd $PATH_TO_SEHEIAH/program
./seheiahd.py start
exit 0
