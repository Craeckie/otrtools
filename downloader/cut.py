#!/usr/bin/python3
# from sys import argv
import argparse
import re, subprocess, os, shutil, sys, traceback
from urllib3 import util as url_util
from .decrypt import decrypt
from .cut_util import cut, cut_video, get_real_name, parse_media_name
from django.conf import settings
from .merge import merge
from .download_util import amazon_upload
from .cutlist import get_cutlist

script_path = os.path.dirname(os.path.realpath(__file__))


def cut(video, cutlist_path, video_base, audio=None, destName=None, keepTemp=False):
    if not os.path.exists(video_base):
        os.mkdir(video_base)
    cutlist = get_cutlist(cutlist_path, video_base)

    video_info = parse_media_name(video).groups()
    if not video_info:
        print("Couldn't parse OTR video name!")
        return None

    # If audio file passed, merge it with video
    if audio:
        dest = merge(video, audio, video_base)
        if not dest:
            return False
        else:
            video = dest
    # Get list of key frames
    print("Searching all keyframes..")

    res = subprocess.check_output([settings.CUT_KEYFRAME_LISTER, video])

    keyframe_list = res.decode("UTF-8").splitlines()
    # else:
    #   keyframe_list = []
    #   print("Could not retrieve list of key frames!\nNo key frame accurate cutting possible :()")

    meta_comment = "Video: " + video + " \nCutlist:\n" + cutlist
    # The cutting into pieces
    cut_files = None
    try:
        (cut_files, concat_list_path) = cut_video(settings.CUT_ENCODER, cutlist, video, video_base, keyframe_list,
                                                  meta_comment)
    except Exception as e:
        print(f"Cutting failed!")
        traceback.print_exc()

    destPath = None
    if cut_files:
        if len(cut_files) == 0:  # No cut in cutlist
            print("Error: No cuts found in cutlist!")
            return False
        if not os.path.exists(settings.DEST_DIR):
            os.mkdir(settings.DEST_DIR)
        if not destName:
            destName = get_real_name(video, settings.DEST_EXT)
        destPath = os.path.abspath(os.path.join(settings.DEST_DIR, destName))

        print(f'Saving to "{destPath}"')
        if len(cut_files) > 1:
            # concatenate the cuts
            extra_flags = []
            if video.endswith(".avi"):
                extra_flags += ["-fflags", "+genpts"]
            if video_info and \
                    settings.CUT_EXT == "mkv" and \
                    any(ext in video_info['extension'] for ext in ('HQ', 'HD')):
                print("Converting with h264_mp4toannexb")
                extra_flags += ['-bsf:v', 'h264_mp4toannexb']
            args = [settings.CUT_ENCODER,
                    '-hide_banner',
                    '-f', 'concat'] + extra_flags + ['-i', concat_list_path,
                                                     '-c:v', 'copy',
                                                     '-c:a', 'copy',
                                                     '-map', '0',
                                                     '-metadata', 'comment=' + meta_comment,
                                                     '-y', destPath]
            print("Arguments: %s" % str(args))
            res = subprocess.call(args);

            if res != 0:
                print("Concatenation failed!")
                return False

            os.remove(concat_list_path)

            # Remove cut files
            # for cur_cut_file in cut_files:
            #   print("Removing " + cur_cut_file)
            #   os.remove(cur_cut_file)

        elif len(cut_files) == 1:
            print("Only one cut, just moving cut file")
            shutil.move(cut_files[0], destPath)
        print(f"Video saved to {destPath}")

        # Fix permissions?
        # shutil.chown(destPath, user="www-data", group="www-data")
        if not keepTemp:
            print("Removing video base at " + os.path.abspath(video_base))
            shutil.rmtree(video_base)
    else:
        print("Cutting failed!")

    return destPath


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("-m", "--mega",
    #                     help="Set to upload video to MEGA",
    #                     action="store_true")
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
    video = args.video
    audio = args.audio
    cutlist = args.cutlist

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

    # os.chdir(video_base)

    dest = cut(video, cutlist, video_base, audio, keepTemp=args.keep)

    if dest:
        print(f"Cutting finished! Saved to {dest}")
    else:
        print("Cutting failed!")
        sys.exit(1)
