import os
from urllib import parse, request

def get_cutlist(path, video_base=None):
    # isDownloaded = False
    cutlist_url = parse.urlparse(path)
    cutlist = None
    if cutlist_url.scheme == 'http':
      file = request.urlopen(path)
      cutlist_b = file.read()
      cutlist = cutlist_b.decode('ISO-8859-1')
      if video_base:
          cutlist_path = os.path.join(video_base, 'cur_cutlist.cutlist')
          output = open(cutlist_path, 'wb')
          output.write(cutlist_b)
          output.close()
    else:
        if os.path.exists(path):
          with open(path, 'r', encoding = 'ISO-8859-1') as f:
            cutlist = f.read()
        else:
          raise Exception(f"Cutlist does not exists: {cutlist}!")
      # cutlist = os.path.realpath(path)
    return cutlist
