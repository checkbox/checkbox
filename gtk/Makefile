top_srcdir = ..

all: hwdb-client-ng-gtk.desktop hwdb-client-ng-gtk-mime.desktop

%.desktop : %.desktop.in
	intltool-merge -d ${top_srcdir}/po/ $< $@

clean:
	rm -f *.desktop
