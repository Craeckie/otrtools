
/*
FFMS_WriteTimecodes - writes timecodes for the given track to disk
Writes Matroska v2 timecodes for the track represented by the given FFMS_Track to the given file. Only meaningful for video tracks.
*/

#include <stdlib.h>
#include <stdio.h>
#include <ffms.h>
#include <inttypes.h>

int main (int argc, const char *argv[]) {
  const char *sourcefile;
  FILE *keyFrameFile = NULL;
  if (2 == argc) {
    sourcefile = argv[1];
    fprintf(stderr, "Source: %s\nDest: stdout\n", sourcefile);
  } else if (3 == argc) {
    sourcefile = argv[1];
    const char *keyframeFilePath = argv[2];

    keyFrameFile = fopen(keyframeFilePath, "w");
    if (keyFrameFile == NULL)
    {
        printf("Error opening keyframe file!\n");
        exit(1);
    }
    printf("Source: %s\nDest: %s\n", sourcefile, keyframeFilePath);
  } else {
    printf("Usage: keyframe-list <input video file> [output keyframe file]\n");
    exit(1);
  }



  /* Initialize the library. */
  FFMS_Init(0, 0);

  /* Index the source file. Note that this example does not index any audio tracks. */
  char errmsg[1024];
  FFMS_ErrorInfo errinfo;
  errinfo.Buffer      = errmsg;
  errinfo.BufferSize  = sizeof(errmsg);
  errinfo.ErrorType   = FFMS_ERROR_SUCCESS;
  errinfo.SubType     = FFMS_ERROR_SUCCESS;

  FFMS_Indexer *indexer = FFMS_CreateIndexer(sourcefile, &errinfo);
  if (indexer == NULL) {
    /* handle error (print errinfo.Buffer somewhere) */
  }

  FFMS_Index *index = FFMS_DoIndexing2(indexer, FFMS_IEH_ABORT, &errinfo);
  if (index == NULL) {
    /* handle error (you should know what to do by now) */
  }

  /* Retrieve the track number of the first video track */
  int trackno = FFMS_GetFirstTrackOfType(index, FFMS_TYPE_VIDEO, &errinfo);
  if (trackno < 0) {
    /* no video tracks found in the file, this is bad and you should handle it */
    /* (print the errmsg somewhere) */
  }
  FFMS_Track *track = FFMS_GetTrackFromIndex(index, trackno);
  if (track == NULL) {
    /* handle error */
  }
  const FFMS_TrackTimeBase *trackTimeBase = FFMS_GetTimeBase(track);

  /* We now have enough information to create the video source object */
  FFMS_VideoSource *videosource = FFMS_CreateVideoSource(sourcefile, trackno, index, 1, FFMS_SEEK_NORMAL, &errinfo);
  if (videosource == NULL) {
    /* handle error */
  }

  /* Since the index is copied into the video source object upon its creation,
  we can and should now destroy the index object. */
  FFMS_DestroyIndex(index);
  index = NULL;

  /* Retrieve video properties so we know what we're getting.
  As the lack of the errmsg parameter indicates, this function cannot fail. */
  const FFMS_VideoProperties *videoprops = FFMS_GetVideoProperties(videosource);

  /* Now you may want to do something with the info, like check how many frames the video has */
  int num_frames = videoprops->NumFrames;

  /* Get the first frame for examination so we know what we're getting. This is required
  because resolution and colorspace is a per frame property and NOT global for the video. */
  const FFMS_Frame *propframe = FFMS_GetFrame(videosource, 0, &errinfo);


  int framenumber;
  // retrieve all key frames
  for (framenumber = 0; framenumber < num_frames; framenumber++) {
    const FFMS_FrameInfo * frameInfo = FFMS_GetFrameInfo(track, framenumber);
    if (0 != frameInfo->KeyFrame) {
      int64_t timestamp = (int64_t)((frameInfo->PTS * trackTimeBase->Num) / (double)trackTimeBase->Den);
      if (keyFrameFile == NULL)
        printf("%d:%" PRId64 "\n", framenumber, timestamp);
      else
        fprintf(keyFrameFile, "%d\n", framenumber);
    }
  }

  if (keyFrameFile != NULL) {
    fclose(keyFrameFile);
  }

  FFMS_DestroyVideoSource(videosource);

  return 0;
}
