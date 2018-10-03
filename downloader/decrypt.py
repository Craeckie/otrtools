#!/usr/bin/python3
import re, os, subprocess
from django.conf import settings

def getDecryptedName(otrkey):
    if not otrkey:
        return None
    name_m = re.match("^(.*)\.otrkey$", otrkey)
    if not name_m:
        print("Not an otrkey file!")
        return None
    else:
        return name_m.group(1)

def decrypt(otrkey, dest):
    if os.path.exists(dest):
        print(f"Destination already exists at {dest}, removing..")
        os.path.remove(dest)

    print(f"Decrypting {otrkey} to {dest}")
    args = [
      "otrtool",
      "-fx",
      '-u', # remove otrkey after decryption
      '-C', settings.OTRKEY_CACHE,
      '-O', dest,
      "-e", settings.OTR_USERNAME,
      "-p", settings.OTR_PASSWORD,
      otrkey
    ]
    print(' '.join(args))
    prc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(prc.stdout.readline, ""):
        if prc.poll() != None:
          break
        # text = line.decode().replace('\n', '')
        # print(text, end='\r')
        print(line.decode(), end='')
    (std, err) = prc.communicate()
    print("")
    prc.stdout.close()
    return_code = prc.wait()
    if return_code == 0 and os.path.exists(dest):
        print("Decryption successful!")
        return True
    else:
        print(f"Decryption failed!")
        if err:
          print(f"Error: {err}")
        return False
