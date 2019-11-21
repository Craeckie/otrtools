#!/usr/bin/python3
import os, subprocess
from multiprocessing.pool import ThreadPool
from .cut_util import parse_media_name
from .waiter import get_dl_url

def prepare_download(video, session, dest_path, audio=None, restart_args=None):
    listfile = f"{video.get_decrypted(dest_path)}.txt"
    print(f"Preparing download. Listfile: {listfile}")
    if os.path.exists(listfile):
        print(f"Removing old listfile at {listfile}")
        os.remove(listfile)
    # requiresDownload = False
    pool = ThreadPool(processes=2)
    results = []
    print(f"video.decrypted: {video.get_decrypted(dest_path)}")
    if audio:
        print(f"audio.decrypted: {audio.get_decrypted(dest_path)}")
    if os.path.exists(video.get_decrypted(dest_path)):
        print("Video already decrypted")
    else:# not os.path.exists(video.get_otrkey(dest_path)):
        results.append(pool.apply_async(get_dl_url, (video.url, session, video.get_otrkey(), restart_args)))
    if audio and os.path.exists(audio.get_decrypted(dest_path)):
      print("Audio already decrypted")
    elif audio:# and not os.path.exists(audio.get_otrkey(dest_path)):
        results.append(pool.apply_async(get_dl_url, (audio.url, session, audio.get_otrkey(), restart_args)))
        # add_download_list(listfile, audio.url, dest_path, audio.get_otrkey())
          # requiresDownload = True
    if not results:
        return None
    for r in results:
        if r:
            (url, otrkey) = r.get()
            print(f"New url: {url} for {otrkey}")
            add_download_list(listfile, url, dest_path, otrkey)
        else:
            print("No result returned from waiter!")
    return listfile

def add_download_list(listfile, url, dest_path, filename):
    print(f"Adding {url} to download list at {listfile}")
    with open(listfile, 'a') as f:
      f.write(f"{url}\n dir={dest_path}\n out={filename}\n")
      return listfile

def download(listfile, video, dest_path, audio=None):
    dl_parts = 4
    if any('otr-files.de/' in url for url in [video.url, audio.url if audio else None] if url):
        print("Only using one download part!")
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

    for i in range(3):
        prc = subprocess.Popen(args, stdout=subprocess.PIPE)
        for line in iter(prc.stdout.readline, ""):
            if prc.poll() != None:
              # print(f"Poll is {prc.poll()}!")
              break
            text = line.decode().replace('\n', '')
            if text.startswith("["):
              print(text, end='\r')
        print("Process exited!")
        print("")
        prc.stdout.close()
        return_code = prc.wait()
        if return_code == 0:
            return return_code
        else:
            print("Download failed! Removing downloaded and trying again..")
            try:
                os.remove(video.get_otrkey(dest_path))
            except FileNotFoundError:
                pass
            if audio:
                try:
                  os.remove(audio.get_otrkey(dest_path))
                except FileNotFoundError:
                    pass
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
