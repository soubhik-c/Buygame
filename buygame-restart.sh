#!/bin/bash

set +x

cd /home/buygame/file_storage

highestnum=$(( $(ls -ld restart-*-data | sed -r 's#restart-([[:digit:]]+)-data#\1#g' | wc -l) + 1 ))

newfoldernm="restart-${highestnum}-data"

echo "Stopping buygame service..."
service buygame stop

mv data $newfoldernm

mkdir data
chmod 777 data

chown -R buygame:buygame $newfoldernm
chmod 400 $newfoldernm

echo "Starting buygame service..."
service buygame start


service buygame status
