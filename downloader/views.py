from django.shortcuts import render
from django.http import HttpResponse
from .process import process

# Create your views here.
def add(request):
    if request.method.lower() == "post":
        video = request.POST.get("Video")
        audio = request.POST.get("Audio")
        cutlist = request.POST.get("Cutlist")
        mega = request.POST.get("Mega", False)
        if video and cutlist:
            ctx = {}
            if not process(video, cutlist, audio_url=audio, mega=mega, keep=False):
                ctx['failed'] = True
            return render(request, 'downloader/index.html', {})
        # function process($video, $audio, $cutlist, $mega) {
        #   $mega_param = $mega == "yes" ? "-m" : "";
        #   $output = shell_exec("run_process $mega_param \"$video\" \"$audio\" \"$cutlist\"");
        #   $key = "Otrkey: ";
        #   $key_len = strlen($key);
        #   foreach(preg_split("/((\r?\n)|(\r\n?))/", $output) as $line) {
        #     if (substr($line, 0, $key_len) === $key) {
        #       $otrkey = substr($line, $key_len);
        #       break;
        #     }
        #   }
        #   $output = substr($output, 0, strlen($output) - 1); // remvoe last newline
        #
        #   $output = nl2br($output);
        #   //echo "<code>Otrkey:" . $otrkey . "<br>";
        #   echo $output . "</code><br><br>";
        #   return $otrkey;
        # }
    else:
        return render(request, 'downloader/index.html', {})
        #return HttpResponse("Hello, world. You're at the downloader.")
