
# pip install -U "steam[client]"
from steam.client import SteamClient
import subprocess
import logging
import subprocess
import requests
from datetime import datetime
from pathlib import Path
import vdf
import sys

import faulthandler
import signal

faulthandler.register(signal.SIGUSR1, all_threads=True)

SCRIPT_PATH = Path(__file__).parent.resolve()
LOG_FILE = SCRIPT_PATH / "service.log"
GAME_PATH = Path("~/games/ArmaReforgerServer").expanduser()
MANIFEST_PATH = GAME_PATH / "steamapps" / "appmanifest_1874900.acf"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)


def getInstalledBuildId() -> int:
    try:
        with open(MANIFEST_PATH, "r") as f:
            manifest = vdf.load(f)
        installedBuildId = manifest['AppState']['buildid']
        logging.info(f"\tInstalled build ID found: {installedBuildId}")
        return int(installedBuildId)
    except Exception as e:
        logging.error(f"\tError reading installed build ID: {e}")
        raise

def getCurrentBuildId() -> int:
    try:
        client = SteamClient()
        client.cli_login("BAXEN_SERVER", "D5MqSRRRbWrsYHv7uSBixABvK0J6DnwWnFHbod5o")
        app_info = client.get_product_info(apps=[1874900])
        currentBuildId = app_info["apps"][1874900]["depots"]["branches"]["public"]["buildid"]
        logging.info(f"\tCurrent build ID from Steam: {currentBuildId}")
        return int(currentBuildId)
    except Exception as e:
        logging.error(f"\tError fetching current build ID: {e}")
        raise

def updateArma():
    result = subprocess.run(["docker", "container", "list", "-a", "--format", "{{.Names}} {{.State}}"], capture_output=True, text=True)
    output = result.stdout
    servers = [(
        server_line.split(" ", 1)[0],
        server_line.split(" ", 1)[1] == "running"
    ) for server_line in output.splitlines() if "arma-reforger" in server_line]

    # Stop all servers that are running
    for server_name, is_running in servers:
        if not is_running:
            continue
        logging.info(f"\tStopping container: {server_name}")
        subprocess.run(["docker", "container", "stop", server_name])

    # update
    # log update
    logging.info(f"\tUpdating arma")
    subprocess(["steamcmd", "+exit"])
    subprocess(["sudo", "-i", "-u", "armaServer",
        "steamcmd", "+force_install_dir", str(GAME_PATH), "+login", "anonymous",
        "+app_update", "1874900", "validate", "+exit"])

    # Start all servers that were running
    for server_name, is_running in servers:
        if not is_running:
            continue
        logging.info(f"\tStarting container: {server_name}")
        subprocess.run(["docker", "container", "start", server_name])

def sendWarning():
    webhooks = [
        "https://discord.com/api/webhooks/1466452645567922277/dfNPiFiN0mf5uyNRmQbTygkEUKrs1zz9BZOcj7M4annjkEm0ak2V8AVk-FhFimHgbDTL",
        "https://discord.com/api/webhooks/1442745220088201337/ZN1g7uDkA9y9Y7BEYcJQJJ-4wwJjUDGQJcLNe1EvHhG7U7YU2M7zDb0xbcDITJAxt4_G"
    ]
    message = "WARPIG2 attempted and failed to update the arma servers\n<@295726442208165889> <@673238422961258535> <@1036118715592355891>"
    author = "WARPIG2 ARMA UPDATER"
    timestamp = datetime.now().isoformat()[0:-3] + "Z"
    data = {
        "content": None,
        "embeds": [
            {
                "description": message,
                "color": 16515072,
                "author": {
                    "name": author
                },
                "timestamp": timestamp
            }
        ]
    }
    for webhook in webhooks:
        requests.post(webhook, json=data)

def main():
    try:
        subprocess(["mkdir", "-p", str(GAME_PATH)])
        logging.info("Running CHECK FOR UPDATE ARMA")
        installedBuildId = getInstalledBuildId()
        currentBuildId = getCurrentBuildId()
        logging.info(f"\tInstalled Build ID: {installedBuildId}, Current Build ID: {currentBuildId}, Up-to-date: {installedBuildId == currentBuildId}")
        print(installedBuildId, currentBuildId, installedBuildId == currentBuildId)
        if installedBuildId != currentBuildId:
            logging.info("\tRunning Update")
            updateArma()
        else:
            logging.info("\tNo update detected")
    except Exception as e:
        logging.error(f"\tScript failed: {e}")
        sendWarning()

if __name__ == "__main__":
    main()


