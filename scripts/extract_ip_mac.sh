#!/bin/bash

for i in *
do
    if test -f "$i"
    then
        echo "Extracting IP and MAC from $i"
        tshark -r $i -T fields -e eth.src -e ip.src -e eth.dst -e ip.dst > tmp.txt
        sort -u tmp.txt >> mac_ip.txt
    fi
done
