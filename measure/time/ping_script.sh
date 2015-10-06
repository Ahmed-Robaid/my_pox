#!/bin/bash

    for i in `seq 1 200`;
    do
        output="$(ping -c1 10.0.0.5)"
        arp -d 10.0.0.5
        sleep 1 
        echo $output | egrep -o "time=[0-9]+.[0-9]+"| egrep -o "[0-9]+.[0-9]+"
    done
