#!/usr/bin/python3
import os, subprocess
from .cut_util import parse_media_name

def add_download_list(listfile, url, dest_path, filename):
    print(f"Adding {url} to download list at {listfile}")
    with open(listfile, 'a') as f:
      f.write(f"{url}\n dir={dest_path}\n out={filename}\n")
      return listfile

def download(listfile, video_url, audio_url=None):

    dl_parts = 4
    if any('otr-files.de/' in url for url in [video_url, audio_url] if url):
        dl_parts = 1
    args = [
      'aria2c',
      '-x', str(dl_parts),
      '--follow-torrent=mem',
      '--max-download-limit=50M',
      '--summary-interval=1',
      '--always-resume', 'false',
      '--auto-file-renaming', 'false',
      '--max-resume-failure-tries=2',
      '--continue=true',
      '-i', listfile]
    print(' '.join(args))
    prc = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in iter(prc.stdout.readline, ""):
        if prc.poll() != None:
          print(f"Poll is {prc.poll()}!")
          break
        text = line.decode().replace('\n', '')
        if text.startswith("["):
          print(text, end='\r')
    print("Process exited!")
    print("")
    prc.stdout.close()
    return_code = prc.wait()
    return return_code

def amazon_upload(file):

    # Upload to mega
    #print("Uploading to mega..")
    #res = subprocess.call(["megaput", mega_path, dest_path])
    # Upload to Amazon Drive
    print("Uploading to amazon drive..")
    res = subprocess.call(["ncftpput", "-t", "300", "-P", "2021", "acd", "/var/decr/josia/Videos/", dest_path])
    if res != 0:
        print("Upload to amazon drive failed!")
        return False
    else:
        return True
