live-visualization
==================

Visualization tool for arbitrary timeseries data routed via Spacebrew and visualized with d3.js
You need Spacebrew, node, and python installed for this to work. 

from the command line do "./run.sh" to launch a server sending randomized data, and then open "Live Visualization/index.html?server=localhost" (the last part should be in the URL you see) in your browser and it should start drawing a graph of the data routed through spacebrew. This is based on Marion's mock server and the rickshaw library on d3.js.
