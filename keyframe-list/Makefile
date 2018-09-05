ifeq ($(PREFIX),)
  PREFIX := /usr
endif

CC=gcc
LIBS=-lffms2
keyframecut: keyframe-list.c
	$(CC) -o keyframe-list keyframe-list.c $(LIBS)
install: keyframe-list
	install -d $(DESTDIR)$(PREFIX)/bin/
	install -m 755 keyframe-list $(DESTDIR)$(PREFIX)/bin/
clean: 
	rm keyframe-list
