#!/bin/bash

cd ./Spacebrew-spacebrew-672a874/
killall node
node node_server_forever.js &
sleep 1
node node_server_forever.js -p 9002 &
sleep 1
cd ../cloudbrain-master/listeners/
python biodata_spacebrew_client.py 
#open "file://${wd}/Live Visualization/index.html?server=localhost"
