#!/bin/bash

for j in `seq 2 30`;
do
    echo "  10.0.0.$j"
    for i in `seq 1 30`;
    do
        sleep 3
        # echo "10.0.0.$j"
        arp -d 10.0.0.$j
        output="$(ping -c1 10.0.0.$j)"
        echo $output | egrep -o "time=[0-9]+.[0-9]+"| egrep -o "[0-9]+.[0-9]+"
    done
done
