
#!/bin/bash
sudo apt install python3 python3-pip python3-venv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
deactivate

sudo cp checkForUpdate.service /etc/systemd/system/checkForUpdate.service
sudo cp checkForUpdate.timer /etc/systemd/system/checkForUpdate.timer
sudo systemctl daemon-reload
sudo systemctl enable checkForUpdate.service checkForUpdate.timer
sudo systemctl start checkForUpdate.service checkForUpdate.timer
