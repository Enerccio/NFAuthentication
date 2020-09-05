import argparse
import random
import datetime
import json
import base64
import os
import tempfile
import websocket
import urllib.request as urlreq

from Crypto.Cipher import AES
from Crypto.Util import Padding


def get_timestamp():
    now = datetime.datetime.utcnow()
    future = now + datetime.timedelta(days=5)
    return int((future - datetime.datetime(year=1970, month=1, day=1)).total_seconds())


parser = argparse.ArgumentParser(description="Creates encrypted key to be used with netflix plugin")
parser.add_argument("output", metavar="output", help="Output file")

args = parser.parse_args()
pin = random.randint(1000, 9999)

user_dir = tempfile.mkdtemp()
port = random.randint(45000, 55000)

os.popen("chromium -incognito --user-data-dir=%s --remote-debugging-port=%s" % (user_dir, str(port)))
input("Navigate to netflix and login, then press enter...")

debuginfos = urlreq.urlopen("http://localhost:" + str(port) + "/json").read()
debuginfo = json.loads(debuginfos)
websocketinfo = debuginfo[0]["webSocketDebuggerUrl"]

wsreq = json.dumps({
    "id": 1,
    "method": "Network.getAllCookies",
    "params": {}
})

ws = websocket.create_connection(websocketinfo)
ws.send(wsreq)
resp_raw = ws.recv()

cookies = json.loads(resp_raw)["result"]["cookies"]

data_content = {
    "cookies": cookies
}

data = {
    "app_name": "NFAuthenticationKey",
    "app_version": "1.0.0.0",
    "app_system": "Windows",
    "app_author": "CastagnaIT",
    "timestamp": get_timestamp(),
    "data": data_content
}

serdata = json.dumps(data)
encoded = Padding.pad(serdata.encode("utf-8"), block_size=16)

iv = '\x00' * 16
encryptor = AES.new((str(pin) + str(pin) + str(pin) + str(pin)).encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))

edata = encryptor.encrypt(encoded)
open(args.output, 'wb').write(base64.encodebytes(edata))

print("Your pin is: " + str(pin))
