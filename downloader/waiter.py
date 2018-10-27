#!/usr/bin/python3
# import urllib3
import time, re, argparse
from urllib.parse import urlparse
import requests
from django.conf import settings

url="https://otr.datenkeller.net/?getFile=The_100__Praimfaya_17.05.24_21-00_uswpix_60_TVOON_DE.mpg.HD.avi.otrkey"

session = requests.session()

def _datenkeller(url, otrkey=None):
    print("Parsing download link from otr.datenkeller.net")
    m = re.search('(?P<url>https?://otr.datenkeller.net/)?.*file=(?P<file>[^&]+)', url)
    if m:
        old_url = url
        session.head(old_url) # to get the cookies
        url = m.expand('\g<url>?getFile=\g<file>')

    invalid_state_count = 0
    while True:
      content = session.get(url).text
      # e.g.: <a href="#" onclick="startCount(3 , 6, 'c270917a85b5efef5cafb8c6350fd9ad', 'cluster.lastverteiler.net',  'The_100__The_Chosen_17.05.17_21-00_uswpix_60_TVOON_DE.mpg.HQ.avi.otrkey');
      match = re.search("<a href=\"#\" onclick=\"startCount\([0-9]+[ ,]+[0-9]+[ ,]+'([a-zA-Z0-9]+)'[ ,]+'([a-zA-Z0-9.-]+)'[ ,]+'([A-Za-z_0-9.-]+\.otrkey)'", content)
      if match:
        print("Got the link!", flush=True)
        access_id = match.group(1)
        server = match.group(2)
        filename = match.group(3)
        dl_url = "http://" + server + "/" + access_id + "/" + filename
        print("Url: " + dl_url, flush=True)
        print("Just waiting another 5 seconds..")
        time.sleep(5)
        return (dl_url, otrkey)
      else:
        match = re.search("<tr bgcolor=lightgrey><td>Deine Position in der Warteschlange: </td><td>([^<]+)</td></tr>", content)
        if match:
            print("Waiting in Queue position %s.." % match.group(1), flush=True)
            time.sleep(settings.DATENKELLER_QUEUE_REFRESH)
        else:
            match = re.search("Ups, da ist was schief gelaufen... Geh nochmal auf die", content)
            if match:
              print("Something went wrong, restarting queue..")
              session.get(old_url)
              invalid_state_count += 1
            else:
              print("Warning: Unknown state!", flush=True)
              invalid_state_count += 1
            time.sleep(5)
        if invalid_state_count >= 5:
            print(content)
            raise RuntimeError(f"Error occurred when waiting in Queue of OTR for {otrkey} at URL {url}!")


def _simpleOTR(url, otrkey=None):
    print("Parsing download link from simple-otr-mirror.de")
    content = session.get(url).text
    match = re.search("<font face=Verdana >wanted file: <a href='(?P<url>[^']+)'", content)
    if match:
        print("Got the link!", flush=True)
        dl_url = match.group("url")
        print("Url: " + dl_url, flush=True)
        return (dl_url, otrkey)
    else:
        raise Exception(f"Couldn't parse URL for {otrkey}:\n{content}")

def get_dl_url(url, otrkey=None):
    print(f"get_dl_url for {url}")
    if not url:
        return url
    h = session.head(url, allow_redirects=True)
    new_url = h.url
    print(f"Redirected to {new_url}")

    new_parse_url = urlparse(new_url)
    hostname = new_parse_url.hostname

    if hostname == 'otr.datenkeller.net':
        return _datenkeller(new_url, otrkey)
    elif hostname == 'simple-otr-mirror.de':
        return _simpleOTR(new_url, otrkey)
    else:
        if urlparse(url).hostname == 'otrkeyfinder.com':
            raise NotImplementedError(f"Can not handle mirror {new_parse_url.hostname}!")
        else:
            return (new_url, otrkey)



if __name__ == 'main':
    parser = argparse.ArgumentParser()
    parser.add_argument("url",
                        help="URL to request download link from otr.datenkeller.at")
    args = parser.parse_args()
    get_dl_url(args.url)
