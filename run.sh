#!/bin/bash

wd=`pwd`
cd ./Spacebrew-spacebrew-672a874/
node node_server_forever.js &
sleep 1
cd ../cloudbrain-master/connectors/spacebrew/
python example_spacebrew_server.py 
#open "file://${wd}/Live Visualization/index.html?server=localhost"
