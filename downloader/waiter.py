#!/usr/bin/python3
# import urllib3
import time, re, argparse
from urllib.parse import urlparse
import requests
from django.conf import settings

from downloader import process

# session = requests.session()

def _datenkeller(url, session, otrkey=None):
    print("Parsing download link from otr.datenkeller.net")
    m = re.search('(?P<url>https?://otr.datenkeller.net/)?.*file=(?P<file>[^&]+)', url)
    if m:
        old_url = url
        session.head(old_url)  # to get the cookies
        url = m.expand('\g<url>?getFile=\g<file>')

    invalid_state_count = 0
    while True:
        content = session.get(url).text
        # e.g.: <a href="#" onclick="startCount(3 , 6, 'c270917a85b5efef5cafb8c6350fd9ad', 'cluster.lastverteiler.net',  'The_100__The_Chosen_17.05.17_21-00_uswpix_60_TVOON_DE.mpg.HQ.avi.otrkey');
        match = re.search(
            "<a href=\"#\" onclick=\"startCount\([0-9]+[ ,]+[0-9]+[ ,]+'([a-zA-Z0-9]+)'[ ,]+'([a-zA-Z0-9.-]+)'[ ,]+'([A-Za-z_0-9.-]+\.otrkey)'",
            content)
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
            match = re.search(
                "<tr bgcolor=lightgrey><td>Deine Position in der Warteschlange: </td><td>([^<]+)</td></tr>", content)
            if otrkey:
                print(otrkey[:25] + '..: ', end='')
            if match:
                print("Waiting in Queue position %s.." % match.group(1), flush=True)
                time.sleep(settings.DATENKELLER_QUEUE_REFRESH)
            else:
                match = re.search("Ups, da ist was schief gelaufen... Geh nochmal auf die", content)
                if match:
                    print(f"Something went wrong, restarting queue (count: {invalid_state_count})..")
                    session.get(old_url)
                    invalid_state_count += 1
                else:
                    print("Warning: Unknown state!", flush=True)
                    invalid_state_count += 1
                time.sleep(settings.DATENKELLER_INVALID_STATE_WAIT)
            if invalid_state_count >= settings.DATENKELLER_INVALID_STATE_RETRY:
                print(content)
                raise RuntimeWarning(f"Error occurred when waiting in Queue of OTR for {otrkey} at URL {url}!")


def _simpleOTR(url, session, otrkey=None):
    print("Parsing download link from simple-otr-mirror.de")
    content = session.get(url).text
    match = re.search("<font face=Verdana >wanted file: <a href='(?P<url>[^']+)'", content)
    if match:
        if otrkey:
            print(otrkey[:25] + '..: ', end='')
        print("Got the link!", flush=True)
        dl_url = match.group("url")
        print("Url: " + dl_url, flush=True)
        return (dl_url, otrkey)
    else:
        raise Exception(f"Couldn't parse URL for {otrkey}:\n{content}")


def get_dl_url(url, session, otrkey=None, restart_args=None):
    print(f"get_dl_url for {url}")
    if not url:
        return url
    h = session.head(url, allow_redirects=True)
    new_url = h.url
    print(f"Redirected to {new_url}")

    new_parse_url = urlparse(new_url)
    hostname = new_parse_url.hostname

    try:
        if hostname == 'otr.datenkeller.net':
            return _datenkeller(new_url, session, otrkey)
        elif hostname == 'simple-otr-mirror.de':
            return _simpleOTR(new_url, session, otrkey)
        else:
            if urlparse(url).hostname == 'otrkeyfinder.com':
                raise NotImplementedError(f"Can not handle mirror {new_parse_url.hostname}! (URL: {new_url})")
            else:
                return (new_url, otrkey)
    except RuntimeWarning as e:
        if restart_args:
            count = 0
            if 'tryCount' in restart_args:
                count = restart_args['tryCount']
            if count < settings.DATENKELLER_INVALID_STATE_REQUEUE:
                count += 1
                print(f"Requeueing {otrkey}, count: {count}!")
                restart_args['tryCount'] = count
                process.process.delay(**restart_args)
                raise RuntimeWarning(f"Requeued {otrkey}, aborting process.")
            else:
                print(f"Reached maximum requeues for {otrkey}. Not retrying!")
                raise e
        else:
            print(f"No restart_args found! Can't requeue {otrkey}!")
            raise e


if __name__ == 'main':
    parser = argparse.ArgumentParser()
    parser.add_argument("url",
                        help="URL to request download link from otr.datenkeller.at")
    args = parser.parse_args()
    get_dl_url(args.url, requests.session())
