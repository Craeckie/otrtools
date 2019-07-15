#!/usr/bin/python3
from celery import shared_task
import re, os, shutil, sys
from argparse import ArgumentParser
from urllib import parse

from downloader.merge import merge
from .decrypt import getDecryptedName, decrypt
from .download_util import prepare_download, download
from .cut_util import parse_base_name, parse_media_name, get_real_name
from .cut import cut
from django.conf import settings

wwwdir = settings.WWW_DIR
# homedir = os.environ['HOME']
# php_path = os.path.join(homedir, 'php/')
# php_path = os.path.join('.', 'php/')

temp_path = settings.CUT_DIR


# regex_otrkey = re.compile("[A-Za-z0-9_-]+([0-9]{2}\.){2}[0-9]{2}_[0-9]{2}-[0-9]{2}_[A-Za-z0-9_]+\.[a-zA-Z4.]+\.otrkey")

class MediaInformation:
    def __init__(self, url):
        self.url = url

    def get_base(self):
        match = parse_base_name(self.url)
        if match:
            return match.group('name')

    def get_otrkey(self, dest_path=''):
        match = parse_media_name(self.url)
        if match:
            return os.path.join(dest_path, match.group(0))

    def get_decrypted(self, dest_path=''):
        otrkey = self.get_otrkey(dest_path)

        return getDecryptedName(otrkey)


@shared_task
def process(video_url, cutlist, audio_url=None, destName=None, keep=False, tryCount=0):
    restart_args = {
        'video_url': video_url,
        'cutlist': cutlist,
        'audio_url': audio_url,
        'destName': destName,
        'keep': keep,
    }
    if not os.path.exists(temp_path): os.mkdir(temp_path)
    video = MediaInformation(video_url)

    base_name = video.get_base()
    if not base_name:
        print(f"Error: couldn't parse base name of \"{video_url}\"")
        return False
    dest_path = os.path.join(temp_path, base_name)
    if not os.path.exists(dest_path): os.mkdir(dest_path)

    audio = None
    if audio_url:
        audio = MediaInformation(audio_url)
        if not audio.get_base():
            print("Error: couldn't parse audio as otrkey format")
            return False

    logpath = video.get_decrypted(settings.LOG_DIR)
    print("Log path: %s" % logpath)
    if os.path.exists(logpath):
        print("Log directory already exists!")
    else:
        print(f"Creating log dir at {logpath}")
        os.makedirs(logpath)
        # for source, dest in {'log-index.php':'index.php', 'read-log.php':'read-log.php'}.items():
        #     srcpath = os.path.join(php_path, source)
        #     destpath = os.path.join(logpath, dest)
        #     print("Copying %s -> %s" %(srcpath, destpath))
        #     shutil.copy(srcpath, destpath)

    print(f"Video:\t{video_url}")
    if audio:
        print(f"Audio:\t{audio_url}")
    if cutlist:
        print(f"Cutlist:\t{cutlist}")
    else:
        print("Culist: None!")
    if destName:
        print(f"Destination:\t{destName}")

    listfile = prepare_download(video, dest_path=dest_path, audio=audio, restart_args=restart_args)

    if listfile:
        if download(listfile, video, dest_path=dest_path, audio=audio) != 0:
            print("Download failed! :(")
            return False
        else:
            if os.path.exists(video.get_otrkey(dest_path)):
                print("Download successful! :)")
                print(f"Removing listfile at {listfile}")
                os.remove(listfile)
            else:
                print("Download finished, but couldn't find downloaded file! :(")
                return False
    else:
        print("Already decrypted, moving forward")

    if not os.path.exists(video.get_decrypted(dest_path)):
        if not decrypt(video.get_otrkey(dest_path), video.get_decrypted(dest_path)):
            return False
    if audio and not os.path.exists(audio.get_decrypted(dest_path)):
        if not decrypt(audio.get_otrkey(dest_path), audio.get_decrypted(dest_path)):
            return False

    # video_path = os.path.join(dest_path, video)
    # audio_path = None
    # if audio:
    #    audio_path = os.path.join(dest_path, audio)

    if cutlist:
        print("Starting cutting..")
        if cut(video.get_decrypted(dest_path), cutlist, video_base=dest_path,
               audio=audio.get_decrypted(dest_path) if audio else None, destName=destName, keepTemp=keep):
            return True
        else:
            print("Cutting failed!")
            return False
    else:
        print("Not cutting!")
        # If audio file passed, merge it with video
        if audio:
            dest = merge(video.get_decrypted(dest_path), audio.get_decrypted(dest_path), video_base)
            if not dest:
                return False
            else:
                video = dest
        else:
            video = video.get_decrypted(dest_path)
        if not destName:
            destName = get_real_name(video, settings.DEST_EXT, isUncut=True)
        destPath = os.path.abspath(os.path.join(settings.DEST_DIR, destName))
        shutil.move(video, destPath)
        if settings.DEST_CHOWN_USER or settings.DEST_CHOWN_GROUP:
            shutil.chown(destPath, user=settings.DEST_CHOWN_USER, group=settings.DEST_CHOWN_GROUP)
        if settings.DEST_CHMOD:
            os.chmod(destPath, settings.DEST_CHMOD)
        print(f"Video saved to {destPath}")
        return True


def main():
    parser = ArgumentParser()
    parser.add_argument("-m", "--mega",
                        help="Set to upload video to MEGA",
                        action="store_true")
    parser.add_argument("video",
                        help="URL to the video to download & cut")
    parser.add_argument("cutlist",
                        help="URL to the cutlist used to cut the video")
    parser.add_argument("-a", "--audio",
                        help="URL to the audio to download, merge and cut")

    args = parser.parse_args()

    video_url = args.video
    if not video_url or parse.urlparse(video_url).scheme not in ['http', 'https', 'ftp', 'ftps']:
        print("A video URL must be provided!")
        return False

    audio_url = args.audio

    cutlist = args.cutlist
    if not cutlist:
        print("A cutlist URL must be provided!")
        return False

    # mega = False
    # if args.m:
    #   mega = True
    #   mega_path = "--path=" + os.environ['mega_path']

    return process(video_url, cutlist, audio_url)


if __name__ == 'main':
    if not main():
        sys.exit(1)
