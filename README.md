live-visualization
==================

Visualization tool for arbitrary timeseries data routed via Spacebrew and visualized with d3.js

<h1>Installation</h1>

You need Spacebrew, node, and python installed for this to work. Also need the following packages in node.js: 

```
npm install ws
npm install forever-monitor
```
and websocket-client in python: 
```
sudo pip install websocket-client
```
Currently running this with 2 local servers (one producing fake data and routing to python client, a 2nd for sending to the visualization after processing is done in that client, along with ECG data & instructions as needed). 

<h1>To Run</h1>

Run 
```
./run.sh
```
from the main directory. And then open up the file <b>./Live Visualization/biodata_visualization.html</b>. Data is currently streaming to the page with the breathing pulse visulazation.

<h1>Manually</h1>

To have the 2 instances of Spacebrew running, do 
```
node node_server_forever.js 
```
from the Spacebrew directory, and then
```
node node_server_forever.js -p 9002
```
to run the 2nd one on port 9002. 
Once these are up, do 
```
python biodata_spacebrew_client.py
```
from the listeners directory in cloudbrew, and FINALLY, open up the biodata_visualization.html file in Live Visualization to start grabbing & plotting data! 

<h1>Debugging</h1>

Check status of spacebrew here:
```
http://spacebrew.github.io/spacebrew/admin/admin.html?server=localhost
```
add 
```
&port=9002 
```
at the end to see the live visualization