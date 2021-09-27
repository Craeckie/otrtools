# NASM (Netwide Assembler)
echo -e "\n\n"
mkdir nasm && cd nasm
echo -n "Downloading nasm.. "
wget -q -O nasm.tar.xz http://www.nasm.us/pub/nasm/releasebuilds/2.13.03/nasm-2.13.03.tar.xz
echo "Done!"
echo -n "Extracting.. "
tar xf nasm.tar.xz --strip-components 1
sed -e '/seg_init/d'                      \
    -e 's/pure_func seg_alloc/seg_alloc/' \
    -i include/nasmlib.h
echo -n "Configuring.. "
./configure --prefix=/usr || exit
echo "Done!"
echo -n "Making.. "
make -j "$CPU_CORES" >make.log || exit
echo "Done!"
echo -n "Installing.. "
make install || exit
echo "Done!"
cd .. && rm -r nasm


# x264
echo -e "\n\n"
mkdir x264 && cd x264
echo -n "Downloading x264.. "
wget -q -O x264-snapshot.tar.bz2 https://download.videolan.org/x264/snapshots/x264-snapshot-20180819-2245-stable.tar.bz2
echo "Done!"
echo -n "Extracting.. "
tar xf x264-snapshot.tar.bz2 --strip-components 1
echo "Done!"
echo -n "Configuring.. "
./configure --prefix=/usr \
            --enable-shared \
            --disable-cli || exit
echo "Done!"
echo -n "Making.. "
make -j "$CPU_CORES" >make.log || exit
echo "Done!"
echo -n "Installing.. "
make install || exit
echo "Done!"
cd .. && rm -r x264

# LAME (mp3)
echo -e "\n\n"
mkdir lame && cd lame
echo -n "Downloading LAME.. "
wget -q -O lame.tar.gz http://downloads.sourceforge.net/lame/lame-3.100.tar.gz || exit 1
echo "Done!"
echo -n "Extracting.. "
tar xf lame.tar.gz --strip-components 1 || exit
echo "Done!"
echo -n "Configuring.. "
# case $(uname -m) in
#    i?86) sed -i -e 's/<xmmintrin.h/&.nouse/' configure ;;
# esac
./configure --prefix=/usr --enable-mp3rtp --enable-nasm --disable-static || exit
echo "Done!"
echo -n "Making.. "
make -j "$CPU_CORES" || exit
echo "Done!"
echo -n "Installing.. "
make install || exit
echo "Done!"
cd .. && rm -r lame

# fdk-aac
echo -e "\n\n"
mkdir fdk-aac && cd fdk-aac
echo -n "Downloading fdk-aac.. "
wget -q -O fdk-aac.tar.gz https://downloads.sourceforge.net/opencore-amr/fdk-aac-0.1.6.tar.gz
echo "Done!"
echo -n "Extracting.. "
tar xf fdk-aac.tar.gz --strip-components 1
echo "Done!"
echo -n "Configuring.. "
./configure --prefix=/usr --disable-static >configure.log || exit
echo "Done!"
echo -n "Making.. "
make -j "$CPU_CORES" >make.log|| exit
echo "Done!"
echo -n "Installing.. "
make install >make.log || exit
echo "Done!"
cd .. && rm -r fdk-aac

# FFMpeg
echo -e "\n\n"
# git clone --depth 1 git://source.ffmpeg.org/ffmpeg.git ffmpeg
mkdir ffmpeg
pushd ffmpeg
wget -q -O ffmpeg.tar.xz http://ffmpeg.org/releases/ffmpeg-4.4.tar.xz
tar xf ffmpeg.tar.xz --strip-components 1

#sed -e '/UPD.*=/,/SET_SCA.*=/d' \
#    -e '/SET_SHA.*=/d' \
#    -e '/GET_LAS.*=/d' \
#    -i libavcodec/libvpxenc.c

#./configure --prefix=/usr        \
#            --enable-gpl         \
#            --enable-version3    \
#            --enable-nonfree     \
#            --disable-static     \
#            --enable-shared      \
#            --disable-debug      \
#            --disable-decoder=vp9 \
#            --disable-encoder=vp9 \
#            --disable-decoder=vp8 \
#             \
#            --enable-libmp3lame \
#            --enable-libx264 &&
./configure --prefix=/usr            \
            --enable-gpl             \
            --enable-version3        \
            --enable-nonfree         \
            --disable-static         \
            --enable-shared          \
            --disable-everything     \
            --disable-debug          \
            --disable-stripping      \
            --enable-libx264         \
            --enable-protocol=file   \
            --enable-muxer=avi       \
            --enable-demuxer=avi     \
            --enable-muxer=mp4       \
            --enable-demuxer=mp4       \
            --enable-muxer=matroska  \
            --enable-demuxer=matroska \
            --enable-muxer=mkvtimestamp_v2 \
            --enable-muxer=matroska_audio  \
            --enable-muxer=h264 \
            --enable-demuxer=h264 \
            --enable-encoder=libx264 \
            --enable-encoder=h264_amf    \
            --enable-encoder=h264_nvenc    \
            --enable-encoder=h264_omx    \
            --enable-encoder=h264_qsv    \
            --enable-encoder=h264_v4l2m2m    \
            --enable-encoder=h264_vaapi    \
            --enable-encoder=h264_videotoolbox    \
            --enable-decoder=h264    \
            --enable-decoder=h264_crystalhd    \
            --enable-decoder=h264_cuvid    \
            --enable-decoder=h264_mediacodec    \
            --enable-decoder=h264_v4l2m2m    \
            --enable-decoder=h264_mmal    \
            --enable-decoder=h264_qsv    \
            --enable-decoder=h264_rkmpp    \
            --enable-encoder=mpeg4    \
            --enable-encoder=mpeg4_v4l2m2m    \
            --enable-decoder=mpeg4    \
            --enable-decoder=mpeg4_crystalhd    \
            --enable-decoder=mpeg4_cuvid    \
            --enable-decoder=mpeg4_mediacodec    \
            --enable-decoder=mpeg4_mmal    \
            --enable-decoder=mpeg4_v4l2m2m    \
            --enable-libmp3lame      \
            --enable-demuxer=mp3     \
            --enable-muxer=mp3       \
            --enable-encoder=mp3     \
            --enable-decoder=mp3     \
            --enable-libfdk-aac      \
            --enable-demuxer=ac3     \
            --enable-muxer=ac3       \
            --enable-encoder=ac3     \
            --enable-decoder=ac3     \
            --enable-decoder=aac     \
            --enable-demuxer=concat  \
            --enable-protocol=concat \
            --enable-bsf=h264_mp4toannexb \
            --enable-bsf=mp3_header_decompress \
            --enable-bsf=chomp       \
            --enable-bsf=aac_adtstoasc \
            --enable-bsf=dump_extradata \
            --enable-bsf=mpeg4_unpack_bframesp \
            --enable-parser=ac3      \
            --enable-parser=h264     \
            --enable-parser=aac      \
            --disable-ffprobe        \
            --disable-doc            &&
make -j "$CPU_CORES" || exit

gcc tools/qt-faststart.c -o tools/qt-faststart

make install || exit

# install -v -m755    tools/qt-faststart /usr/bin # &&
#mkdir -p /usr/share/doc/ffmpeg-2.8.3
#install -v -m644    doc/*.txt \
#                    /usr/share/doc/ffmpeg-2.8.3



cd .. && rm -rf ffmpeg
