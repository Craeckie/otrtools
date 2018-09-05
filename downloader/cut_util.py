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

def get_codec(video):
  m = re.search("TVOON_[A-Z]+\.([.A-Za-z0-9]+)$", video)
  if m:
      ext = m.group(1)
      print(ext)
      return format2codec.get(ext)
  else:
      print("Codec not found for extension: %s!" % ext)
      return None

def cut(encoder, video, concat_file, cut_params, transcode=False, meta_comment=None):
  # if transcode:
  #   print("ok, will start transcoding from %s for %s frames" % (str(cut_params['start_frame']), str(cut_params['dur_frames'])))
  # else:
  print("ok, will start cutting from %s for %s seconds" % (str(cut_params['start_fl']), str(cut_params['dur_fl'])))
  video_name = "cut" + str(cut_params['index']) + "." + ext


  extra_flags = []
  if video.endswith(".avi"):
    extra_flags += ["-fflags", "+genpts"]
  args = [encoder, '-hide_banner']
  #   args += ['-noaccurate_seek']
  # if not transcode:
  args += ['-ss', str(cut_params['start_fl'])]

  args += ['-fflags', '+genpts', '-i', video]
  if transcode:
    args += get_codec(video) + ['-crf', '18', '-preset', 'slower', '-tune', 'film']
    args += ['-ss', '0']
  else:
    args += ['-c:v', 'copy']
  if meta_comment:
    args += ['-metadata', 'comment=' + meta_comment]
  args += ['-t', str(cut_params['dur_fl']),
           '-avoid_negative_ts', '1',
           '-c:a', 'copy',
           '-map', '0',
           '-avoid_negative_ts', '1',

           '-y', video_name]
  print("Arguments: %s" % str(args))
  if subprocess.call(args) != 0:
      print("Call of ffmeg failed! Exiting.")
      sys.exit(1)
  concat_file.write("file '%s'\n" % video_name)
  return video_name

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

  # Search for keyframe after timestamp(390):
  # ffprobe -read_intervals "390%+20" -print_format json -select_streams v -noprivate -show_entries 'frame=key_frame,best_effort_timestamp_time' movie.avi
  # | jq -C '[.frames[] | select(.key_frame == 1) | .best_effort_timestamp_time | tonumber | select(.>=390)] | min'
  # print("Searching for keyframe before " + str(start))
  # start_offset = 10
  # start_cur = start - start_offset
  # cmd=prober + ' -select_streams v -read_intervals ' + str(start_cur) + '%+' + str(start_offset) + ' -show_frames ' + video
  # print("CMD: " + cmd)
  # p = subprocess.Popen(cmd,
  #                   shell=True,
  #                   bufsize=64,
  #                   stdin=subprocess.PIPE,
  #                   stderr=subprocess.PIPE,
  #                   stdout=subprocess.PIPE)
  #
  # pos=''
  # keyframe='0'
  # cur_last_kf=''
  # for line in p.stdout:
  #   tmp = str(line.rstrip())
  #   if tmp.startswith("b'key_frame="):
  #     keyframe = tmp[len("b'key_frame="):len(tmp) - 1]
  #   if tmp.startswith("b'pkt_dts_time="):
  #     pos = tmp[len("b'pkt_dts_time="):len(tmp) - 1]
  #     if float(pos) > start_cur + start_offset:
  #       print("killing ffprobe")
  #       p.kill()
  #   if keyframe != '0' and "b'[/FRAME]" in tmp:
  #     print(pos)
  #     cur_last_kf = pos
  #     pos = ''
  #     keyframe='0'
  #
  # return float(cur_last_kf)

def cut_section(encoder, video, keyframe_list, concat_file, cur_cut, meta_comment=None):
  kf_result = find_keyframe(keyframe_list, cur_cut)
  if kf_result['type'] == KeyframeResult.found:
    # kf_cut = cur_cut
    pre_cut = kf_result['pre_cut_params']
    pre_cut['index'] = '%sa' % cur_cut['index']
    video_name = cut(encoder, video, concat_file, pre_cut, transcode=True, meta_comment=meta_comment)
    cur_cut = kf_result['next_cut']
  elif kf_result['type'] == KeyframeResult.isKeyFrame:
    cur_cut = kf_result['next_cut']

  video_name = cut(encoder, video, concat_file, cur_cut, meta_comment)
  return video_name

def use_cutlist(encoder, cutlist, video, keyframe_list, meta_comment=None):
    print("Openening cutlist at " + cutlist)
    cut_file = open(cutlist, 'r', encoding = "ISO-8859-1")
    concat_file = open("concat_list.txt", 'w');

    i = -1
    start=''
    dur = ''
    cut_files=[]
    cut_text = cut_file.read()
    success = False
    cur_cut = {}

    for cut_line in cut_text.split('\n'):
      #cut_line = re.sub("[^A-Za-z0-9._=\[\]-]+", '', cut_line);
      cut_line = cut_line.rstrip()
      #print(cut_line.encode('utf-8').strip())
      cut_start_match = re.match("\[Cut([0-9]+)\]$", cut_line);
      if cut_start_match:
        if i >= 0 and 'start_fl' in cur_cut and 'dur_fl' in cur_cut:
          # section is finished, need to cut here
          cur_cut['index'] = i
          video_name = cut_section(encoder, video, keyframe_list, concat_file, cur_cut, meta_comment)
          cut_files.append(video_name)
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
      video_name = cut_section(encoder, video, keyframe_list, concat_file, cur_cut, meta_comment)
      cut_files.append(video_name)
      success = True
    cut_file.close()

    if success: # at least one cut found
      concat_file.close()


    return cut_files

def parse_media_name(filename):
    #Southpaw_17.10.10_21-00_ukfilm4_145_TVOON_DE.mpg.HD.avi
    filename_match = re.search('(?P<name>[a-zA-Z0-9_-]+)_(?P<date>[0-9]{2}\.[0-9]{2}\.[0-9]{2})_(?P<time>[0-9]{2}-[0-9]{2})_(?P<sender>[0-9A-Za-z-]+)_(?P<duration>[0-9]+)_TVOON_DE(?P<extension>[A-Za-z0-9.]+)$', filename)
    return filename_match
def parse_base_name(filename):
    basename_match = re.search('(?P<name>[a-zA-Z0-9_-]+_[0-9]{2}\.[0-9]{2}\.[0-9]{2}_[0-9]{2}-[0-9]{2}_[0-9A-Za-z-]+_[0-9]+_TVOON_DE)(?P<extension>[A-Za-z0-9.]+)$', filename)
    return basename_match

def get_real_name(filename):
    dest_path = filename + ext
    filename_match = parse_media_name(filename)
    if filename_match:
      temp_filename = filename_match.group('name')
      actual_filename = re.sub('_', ' ', temp_filename)
      dest_path = actual_filename + '.' + ext #os.path.splitext(video)[0] + ".cut.avi"
    else:
      print("Could not parse OTR-standard filename")
    return dest_path
