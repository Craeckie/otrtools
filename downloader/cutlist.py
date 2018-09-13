import os
from urllib import parse, request

def get_cutlist(path):
    # isDownloaded = False
    cutlist_url = parse.urlparse(path)
    cutlist = None
    if cutlist_url.scheme == 'http':
      file = request.urlopen(path)
      cutlist = file.read().decode('ISO-8859-1')
      # cutlist = os.path.join(video_base, 'cur_cutlist.cutlist')
      # output = open(cutlist, 'wb')

      # output.write(file.read())
      # output.close()
      # isDownloaded = True
    else:
        if os.path.exists(path):
          with open(path, 'r', encoding = 'ISO-8859-1') as f:
            cutlist = f.read()
        else:
          raise Exception(f"Cutlist does not exists: {cutlist}!")
      # cutlist = os.path.realpath(path)
    return cutlist
