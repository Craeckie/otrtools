import os
from urllib import parse, request

def get_cutlist(cutlist):
    # Get the cutlist
    isDownloaded = False
    cutlist_url = parse.urlparse(cutlist)
    if cutlist_url.scheme == 'http':
      file = request.urlopen(cutlist)
      cutlist = os.path.join(video_base, 'cur_cutlist.cutlist')
      output = open(cutlist, 'wb')
      output.write(file.read())
      output.close()
      isDownloaded = True
    else:
      cutlist = os.path.realpath(cutlist)
    return (cutlist, isDownloaded)
