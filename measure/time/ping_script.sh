#!/bin/bash

    for i in `seq 1 200`;
    do
        arp -d 10.0.0.100
        output="$(ping -c1 10.0.0.100)"
        sleep 2 
        echo $output # | egrep -o "time=[0-9]+"| egrep -o "[0-9]+"
    done

