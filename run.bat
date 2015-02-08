cd ./Spacebrew-spacebrew-672a874/
taskkill /F /IM node.exe
taskkill /F /IM python.exe
start node node_server_forever.js 
timeout /t 1 /nobreak
start node node_server_forever.js -p 9002 &
timeout /t 1 /nobreak
taskkill /F /IM wmplayer.exe
REM taskkill /F /IM chrome.exe
start "" "C:\Program Files (x86)\Windows Media Player\wmplayer.exe" "C:\Users\ExplorCogTech\Music\stream.wav"
start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --kiosk
timeout /t 1 /nobreak
cd ..
start python ./cloudbrain-master/listeners/biodata_spacebrew_client.py 
