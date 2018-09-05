#!/usr/bin/python3
import re, os, subprocess
from django.conf import settings


def merge(video, audio, dest):
    if os.path.exists(dest):
        print("Destination already exists, removing..")
        os.path.remove(dest)

    print(f"Merging:\nVideo: {video}\nand\n Audio: {audio}\nTo: {dest}")
    args = [
      settings.CUT_ENCODER,
      '-hide_banner',
      '-fflags', '+genpts',
      '-i',
      video,
      '-fflags', '+genpts',
      '-i',
      audio,
      '-map', '0:0',
      '-map', '1:0',
      '-map', '0:1',
      '-c:v', 'copy',
      '-c:a', 'copy',
      dest
    ]
    print(' '.join(args))
    prc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(prc.stdout.readline, ""):
        if prc.poll() != None:
          break
        text = line.decode()
        print(text)
    (std, err) = prc.communicate()
    print("")
    prc.stdout.close()
    return_code = prc.wait()
    if return_code == 0 and os.path.exists(dest):
        print("Merge successful!")
        return True
    else:
        print(f"Merging failed!")
        if err:
          print(f"Error: {err}")
        return False
