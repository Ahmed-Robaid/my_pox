#!/bin/bash
for j in `seq 10 10 100`;
do
    for i in `seq 1 200`;
    do
        arp -d 10.0.0.$j
        output="$(ping -c1 10.0.0.$j)"
        sleep 1.5
        echo $output | egrep -o "time=[0-9]+.[0-9]+"| egrep -o "[0-9]+.[0-9]+"
    done
done
