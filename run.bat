cd ./Spacebrew-spacebrew-672a874/
taskkill /F /IM node.exe
taskkill /F /IM python.exe
start node node_server_forever.js 
timeout /t 1 /nobreak
start node node_server_forever.js -p 9002 &
timeout /t 1 /nobreak
cd ../cloudbrain-master/listeners/
start python biodata_spacebrew_client.py 
