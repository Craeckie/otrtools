#!/usr/bin/python3
#from sys import argv
import argparse
import re
import subprocess, os, shutil, sys
from urllib3 import util as url_util
from .decrypt import decrypt
from .cut_util import cut, use_cutlist, get_real_name
from django.conf import settings
from .merge import merge
from .download_util import amazon_upload
from .cutlist import get_cutlist

script_path = os.path.dirname(os.path.realpath(__file__))

def cut(video, cutlist, video_base, audio=None):
    # If audio file passed, merge it with video
    if audio:
      tmp_merge_name = "merge." + settings.CUT_EXT
      if not merge(video, audio, tmp_merge_name):
          return False
      print("Removing video(" + video + ") and audio(" + audio + ")")
      os.remove(video)
      os.remove(audio)
      video = os.path.splitext(video)[0] + "." + settings.CUT_EXT
      print("Moving merged video(" + tmp_merge_name + "->" + video)
      os.rename(tmp_merge_name, video)

    # Get list of key frames
    print("Searching all keyframes..")

    res = subprocess.check_output(["keyframe-list", video])

    keyframe_list = res.decode("UTF-8").splitlines()
    # else:
    #   keyframe_list = []
    #   print("Could not retrieve list of key frames!\nNo key frame accurate cutting possible :()")

    meta_comment = "Video: " + video + " \nCutlist: " + cutlist
    # The cutting into pieces
    cut_files = use_cutlist(settings.CUT_ENCODER, cutlist, video, keyframe_list, meta_comment)

    if len(cut_files) == 0: # No cut in cutlist
      print("Error: No cuts found in cutlist!")
      return False
    dest_path = os.path.abspath("../" + get_real_name(video))

    print("Saving to \"" + dest_path + "\"")
    if len(cut_files) > 1:
      # concatenate the cuts
      extra_flags = []
      if video.endswith(".avi"):
        extra_flags = ["-fflags", "+genpts"]
      args = [settings.CUT_ENCODER,
        '-hide_banner',
        '-f', 'concat'] + extra_flags + ['-i', "concat_list.txt",
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-map', '0',
        '-metadata', 'comment=' + meta_comment,
        '-y', dest_path]
      print("Arguments: %s" % str(args))
      res = subprocess.call(args);

      if res != 0:
        print("Concatenation failed!")
        return False
      video = dest_path

      # os.remove("concat_list.txt")

      # Remove cut files
      # for cur_cut_file in cut_files:
      #   print("Removing " + cur_cut_file)
      #   os.remove(cur_cut_file)

    elif len(cut_files) == 1:
      print("Only one cut, just moving cut file")
      os.rename(cut_files[0], dest_path)


    if downl_cutlist:
      print("Removing cutlist at " + cutlist)
      os.remove(cutlist)

    os.chdir("..")
    print("Removing video base at " + os.path.abspath(video_base))
    shutil.rmtree(video_base)
    sender_extension_match = re.search("[A-Za-z0-9_-]+_[0-9]{2}\.[0-9]{2}\.[0-9]{2}_[0-9]{2}-[0-9]{2}_([A-Za-z0-9]+)_[0-9]+_TVOON_[A-Z]+\.(.*)$", os.path.basename(video_base))

    extension = "mpg.avi"
    if sender_extension_match:
        (filename, ext) =  os.path.splitext(os.path.basename(dest_path))
        dest_path = "%s.avi" % filename
        sender = sender_extension_match.group(1)
        extension = sender_extension_match.group(2)
        print("Sender: %s, Extension: %s" % (sender, extension))
        if sender.startswith("uk") or sender.startswith("us"):
            dest_path = "%s (engl).avi" % filename
            print("Is english, new name: %s" % dest_path)

    if ext == "mkv":
      extra_flags = []
      if any(ext in extension for ext in ('HQ', 'HD')):
          print("Converting with h264_mp4toannexb")
          extra_flags = ['-bsf:v', 'h264_mp4toannexb']

      args = [settings.CUT_ENCODER, '-hide_banner', '-i', video,
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-map', '0'] + extra_flags + ['-y', dest_path]
      print("Arguments: %s" % str(args))
      res = subprocess.call(args);

      if res != 0:
        print("Conversion mkv -> avi failed!")
        return False

      os.remove(video)
    else:
      os.rename(video, dest_path)
      video = dest_path

    # Fix permission
    shutil.chown(dest_path, user="www-data", group="www-data")
    return dest_path

if __name__ == 'main':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mega",
                        help="Set to upload video to MEGA",
                        action="store_true")
    parser.add_argument("-d", "--decrypt",
                        help="Set to decrypt the given otrkey file",
                        action="store_true")
    parser.add_argument("-k", "--keep",
                        help="Set to keep (decrypted) video file",
                        action="store_true")
    parser.add_argument("video",
                        help="The video/otrkey to (decrypt and) cut")
    parser.add_argument("cutlist",
                        help="The cutlist used to cut the video (URL or path)")
    parser.add_argument("--audio",
                        help="The audio to merge and cut")
    # parser.add_argument("--megacall", help="The command to upload a video to MEGA")
    args = parser.parse_args()

    if os.path.exists(video):
      video = os.path.realpath(video)
    if not video:
      print("A valid video name or URL must be provided!")
      sys.exit(1)
    if not cutlist:
      print("A cutlist must be provided!")
      sys.exit(1)

    # Create a working directory and move our video here
    if args.decrypt:
        print("Decrypting video..")
        video = decrypt(video)
        if not video:
            print("Decryption of video failed!")
            sys.exit(1)
        if audio:
            print("Decrypting audio..")
            audio = decrypt(audio)
            if not audio:
                print("Decryption of audio failed!")
                sys.exit(1)

    video = args.video
    audio = args.audio

    video_base = re.match("^(.*)\.[a-zA-Z0-9]+$", video).group(1)
    print("Video Base (and cwd): " + video_base)
    if not os.path.isdir(video_base):
        os.mkdir(video_base)
    old_video_path = video
    video = os.path.join(video_base, os.path.basename(video))
    # old_video_path = os.path.join(video, "..")
    print("%s -> %s" % (old_video_path, video))
    if args.keep:
        shutil.copy(old_video_path, video)
    else:
        os.rename(old_video_path, video)

    if audio:
        old_audio_path = audio
        audio = os.path.join(video_base, os.path.basename(audio))
        if args.keep:
            shutil.copy(old_audio_path, audio)
        else:
            os.rename(old_audio_path, audio)

    (cutlist, isDownloaded) = get_cutlist(args.cutlist)

    os.chdir(video_base)

    dest = cut(video, cutlist, video_base, audio)
    if isDownloaded:
        os.remove(cutlist)
    if dest:
        if args.mega:
            mega_path = "--path=" + os.environ['mega_path']
            if amazon_upload(dest):
                print("Succesfully uploaded, removing video")
                os.remove(dest_path)
            else:
                sys.exit(1)
        else:
          print("Not uploading to mega, keeping video file")
    else:
        print("Cutting failed!")
        sys.exit(1)
