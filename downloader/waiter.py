#!/usr/bin/python3
# import urllib3
import time, re, argparse
import requests

url="https://otr.datenkeller.net/?getFile=The_100__Praimfaya_17.05.24_21-00_uswpix_60_TVOON_DE.mpg.HD.avi.otrkey"

def get_dl_url(url):
    # cj = CookieJar()
    # opener = urllib3.build_opener(urllib2.HTTPCookieProcessor(cj))
    session = requests.session()

    while True:
      # response = opener.open(url)
      # content = response.read()
      content = session.get(url).text
      # <a href="#" onclick="startCount(3 , 6, 'c270917a85b5efef5cafb8c6350fd9ad', 'cluster.lastverteiler.net',  'The_100__The_Chosen_17.05.17_21-00_uswpix_60_TVOON_DE.mpg.HQ.avi.otrkey');
      match = re.search("<a href=\"#\" onclick=\"startCount\([0-9]+[ ,]+[0-9]+[ ,]+'([a-zA-Z0-9]+)'[ ,]+'([a-zA-Z0-9.-]+)'[ ,]+'([A-Za-z_0-9.-]+\.otrkey)'", content)
      if match:
        print("Got the link!", flush=True)
        access_id = match.group(1)
        server = match.group(2)
        filename = match.group(3)
        dl_url = "http://" + server + "/" + access_id + "/" + filename
        print("Url: " + dl_url, flush=True)
        time.sleep(5)
        return dl_url
      else:
        match = re.search("<tr bgcolor=lightgrey><td>Deine Position in der Warteschlange: </td><td>([^<]+)</td></tr>", content)
        if match:
            print("Waiting in Queue position %s.." % match.group(1), flush=True)
        else:
            print("Waiting in Queue: %s" % content, flush=True)
        time.sleep(30)

if __name__ == 'main':
    parser = argparse.ArgumentParser()
    parser.add_argument("url",
                        help="URL to request download link from otr.datenkeller.at")
    args = parser.parse_args()
    get_dl_url(args.url)
