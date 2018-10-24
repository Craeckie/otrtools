import re
import subprocess, os, sys
from enum import Enum

ext="avi"
cut_offset_frames = 10
cut_offset_fl = 0.4
format2codec = {
  'mpg.HD.avi': ['-c:v', 'h264', '-tag:v', '0x34363248'],
  'mpg.HQ.avi': ['-c:v', 'h264', '-tag:v', '0x34363248'],
  'mpg.avi': ['-c:v', 'mpeg4', '-tag:v', 'DX50'],
  'mpg.mp4': ['-c:v', 'h264', '-tag:v', 'avc1'],
}
ffmpeg_general_options = [
  '-hide_banner',
  '-loglevel', 'warning',
  '-stats'
]

def get_codec(video):
  m = re.search("TVOON_[A-Z]+\.([.A-Za-z0-9]+)$", video)
  if m:
      ext = m.group(1)
      print(ext)
      return format2codec.get(ext)
  else:
      print("Codec not found for {video}! Using codec for HQ/HD.")
      return format2codec.get('mpg.HQ.avi')

def cut(encoder, video, video_base, concat_file, cut_params, transcode=False, meta_comment=None):
  # if transcode:
  #   print("ok, will start transcoding from %s for %s frames" % (str(cut_params['start_frame']), str(cut_params['dur_frames'])))
  # else:
  # print("Cut_params: %s" % str(cut_params))
  start = cut_params['start_fl']
  duration = cut_params['dur_fl']
  print(f"ok, will start cutting from {start} for {duration} seconds")
  video_name = f"cut{cut_params['index']}.{ext}"
  video_path = os.path.join(video_base, video_name)


  extra_flags = []
  if video.endswith(".avi"):
    extra_flags += ["-fflags", "+genpts"]
  args = [encoder]
  args += ffmpeg_general_options
  #   args += ['-noaccurate_seek']
  # if not transcode:
  args += ['-ss', str(start)]

  args += ['-fflags', '+genpts', '-i', video]
  if transcode:
    args += get_codec(video) + ['-crf', '18', '-preset', 'slower', '-tune', 'film']
    args += ['-ss', '0']
  else:
    args += ['-c:v', 'copy']
  if meta_comment:
    args += ['-metadata', 'comment=' + meta_comment]
  args += ['-t', str(duration),
           '-avoid_negative_ts', '1',
           '-c:a', 'copy',
           '-map', '0',
           '-avoid_negative_ts', '1',
           '-y', video_path]
  print("Arguments: %s" % str(args))
  if subprocess.call(args) != 0:
      print("Running ffmpeg failed!")
      return None
  concat_file.write(f"file '{video_name}'\n")
  return video_path

class KeyframeResult(Enum):
  isKeyFrame = 1
  found = 2
  endOfFile = 3

def find_keyframe(keyframe_list, cut_params):
  result = {}
  for frames in keyframe_list:
    (kf, milliseconds) = tuple([int(x) for x in frames.split(':')])
    use_frames = True
    if 'start_frame' in cut_params:
        start = cut_params['start_frame']
        kf_diff = kf - start
    else:
        start = cut_params['start_fl']
        use_frames = False
        kf_diff = (milliseconds / 1000.) - start
    kf_diff_fl = (milliseconds / 1000.) - start
    if (use_frames and abs(kf_diff) <= 5) or (not use_frames and abs(kf_diff_fl) <= 0.2):
        result['type'] = KeyframeResult.isKeyFrame
        next_cut = cut_params.copy()

        if kf_diff > 0:
            if use_frames:
                print("Next keyframe is just %s frames or %.3f seconds ahead, adjusting cut to be after next keyframe" % (kf_diff, kf_diff_fl))
            else:
                print("Next keyframe is just %.3f seconds ahead, adjusting cut to be after next keyframe" % kf_diff_fl)
            kf_diff += cut_offset_frames
            kf_diff_fl =+ cut_offset_fl
        else:
            if use_frames:
                print("Previous keyframe is just %s frames or %.3f seconds before, adjusting cut" % (kf_diff, kf_diff_fl))
            else:
                print("Previous keyframe is just %.3f seconds before, adjusting cut" % kf_diff_fl)
            kf_diff = 5
            kf_diff_fl = 0.2
        if use_frames:
            next_cut['start_frame'] += kf_diff
            next_cut['dur_frames'] -= kf_diff

        next_cut['start_fl'] += kf_diff_fl
        next_cut['dur_fl'] -= kf_diff_fl
        result['next_cut'] = next_cut

        return result
    elif (use_frames and kf > start) or (not use_frames and (milliseconds / 1000.) > start):
        result['type'] = KeyframeResult.found

        start_fl = cut_params['start_fl']
        end_fl = (milliseconds / 1000.)
        dur_fl = end_fl - cut_params['start_fl']
        result['pre_cut_params'] = {
          'start_fl': str(cut_params['start_fl']),
          'dur_fl': str(dur_fl)
        }
        if use_frames:
            start_frame = cut_params['start_frame']
            end_frame = kf
            dur = end_frame - start_frame
            result['pre_cut_params']['start_frame'] = str(cut_params['start_frame'])
            result['pre_cut_params']['dur_frames'] = str(dur)

        # Calculate next cut starting at keyframe.
        # Duration needs to be shortened by duration of current "pre_cut"
        next_cut = cut_params.copy()
        # Go beyond keyframe, because ffmpeg will seek to keyframe before given timestamp
        if use_frames:
            next_cut['start_frame'] = end_frame + cut_offset_frames
            next_cut['dur_frames'] = cut_params['dur_frames'] - dur
        next_cut['start_fl'] = end_fl + cut_offset_fl
        next_cut['dur_fl'] = cut_params['dur_fl'] - dur_fl
        result['next_cut'] = next_cut
        return result
    else:
        previous_kf = kf
        previous_millis = milliseconds

  result['type'] = KeyframeResult.endOfFile
  return result

def cut_section(encoder, video, video_base, keyframe_list, concat_file, cur_cut, meta_comment=None):
  kf_result = find_keyframe(keyframe_list, cur_cut)
  if kf_result['type'] == KeyframeResult.found:
    # kf_cut = cur_cut
    pre_cut = kf_result['pre_cut_params']
    pre_cut['index'] = '%sa' % cur_cut['index']
    video_path = cut(encoder, video, video_base, concat_file, pre_cut, transcode=True, meta_comment=meta_comment)
    if not video_path:
      return None
    cur_cut = kf_result['next_cut']
  elif kf_result['type'] == KeyframeResult.isKeyFrame:
    cur_cut = kf_result['next_cut']

  video_path = cut(encoder, video, video_base, concat_file, cur_cut, transcode=False, meta_comment=meta_comment)
  return video_path

def cut_video(encoder, cutlist, video, video_base, keyframe_list, meta_comment=None):
    # print("Openening cutlist at " + cutlist)
    # cut_file = open(cutlist, 'r', encoding = "ISO-8859-1")
    concat_list_path = os.path.join(video_base, "concat_list.txt")
    concat_file = open(concat_list_path, 'w');

    i = -1
    start=''
    dur = ''
    cut_files=[]
    # cut_text = cut_file.read()
    success = False
    cur_cut = {}

    for cut_line in cutlist.split('\n'):
      #cut_line = re.sub("[^A-Za-z0-9._=\[\]-]+", '', cut_line);
      cut_line = cut_line.rstrip()
      #print(cut_line.encode('utf-8').strip())
      cut_start_match = re.match("\[Cut([0-9]+)\]$", cut_line);
      if cut_start_match:
        if i >= 0 and 'start_fl' in cur_cut and 'dur_fl' in cur_cut:
          # section is finished, need to cut here
          cur_cut['index'] = i
          video_path = cut_section(encoder, video, video_base, keyframe_list, concat_file, cur_cut, meta_comment)
          if not video_path:
              return (None, concat_list_path)
          cut_files.append(video_path)
          success = True
        i = int(cut_start_match.group(1));
        print("\n---\nCut section " + str(i) +" starts\n---\n")
        cur_cut = {}
      elif i >= 0: # in cut section, try to get values
        match = re.match("Start=([0-9.]+)", cut_line)
        if match:
          cur_cut['start_fl'] = float(match.group(1))
          print("Found start: " + str(cur_cut['start_fl']))

        match = re.match("StartFrame=([0-9]+)", cut_line)
        if match:
          cur_cut['start_frame'] = int(match.group(1))
          print("Found start frame: " + str(cur_cut['start_frame']))

        match = re.match("Duration=([0-9.]+)", cut_line)
        if match:
          cur_cut['dur_fl'] = float(match.group(1))
          print("Found dur: " + str(cur_cut['dur_fl']))

        match = re.match("DurationFrames=([0-9]+)", cut_line)
        if match:
          cur_cut['dur_frames'] = int(match.group(1))
          print("Found duration frames: " + str(cur_cut['dur_frames']))

    if i >= 0 and 'start_fl' in cur_cut and 'dur_fl' in cur_cut:
      # section is finished, need to cut here
      cur_cut['index'] = i
      video_path = cut_section(encoder, video, video_base, keyframe_list, concat_file, cur_cut, meta_comment)
      if not video_path:
          return (None, concat_list_path)
      cut_files.append(video_path)
      success = True

    if success: # at least one cut found
      concat_file.close()


    return (cut_files, concat_list_path)

def parse_media_name(filename):
    #Southpaw_17.10.10_21-00_ukfilm4_145_TVOON_DE.mpg.HD.avi
    filename_match = re.search('(?P<name>[a-zA-Z0-9_-]+)_(?P<date>[0-9]{2}\.[0-9]{2}\.[0-9]{2})_(?P<time>[0-9]{2}-[0-9]{2})_(?P<sender>[0-9A-Za-z-]+)_(?P<duration>[0-9]+)_TVOON_DE(?P<extension>[A-Za-z0-9.]+)', filename)
    return filename_match
def parse_base_name(filename):
    basename_match = re.search('(?P<name>[a-zA-Z0-9_-]+_[0-9]{2}\.[0-9]{2}\.[0-9]{2}_[0-9]{2}-[0-9]{2}_[0-9A-Za-z-]+_[0-9]+_TVOON_DE)(?P<extension>[A-Za-z0-9.]+)', filename)
    return basename_match

def get_real_name(filename, extension):
    dest_path = filename + extension
    filename_match = parse_media_name(filename)
    if filename_match:
      temp_filename = filename_match.group('name')
      actual_filename = re.sub('_', ' ', temp_filename)

      sender = filename_match.group("sender")

      if sender.startswith("uk") or sender.startswith("us"):
          actual_filename += " (engl)"
          print("Is english, new name: %s" % actual_filename)

      dest_path = actual_filename + '.' + extension #os.path.splitext(video)[0] + ".cut.avi"
    else:
      print("Could not parse OTR-standard filename")
    return dest_path
