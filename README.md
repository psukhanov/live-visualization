live-visualization
==================

Visualization tool for arbitrary timeseries data routed via Spacebrew and visualized with d3.js
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

(Will try to simplify process for further development). 
