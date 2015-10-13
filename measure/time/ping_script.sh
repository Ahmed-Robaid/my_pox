#!/bin/bash

    for i in `seq 1 30`;
    do
        arp -d 10.0.0.80
        output="$(ping -c1 10.0.0.80)"
        sleep 12 
        echo $output | egrep -o "time=[0-9]+.[0-9]+"| egrep -o "[0-9]+.[0-9]+"
    done

