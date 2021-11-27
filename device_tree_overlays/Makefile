
all:
	@if [ ! -d bb.org-overlays ]; then\
		git clone https://github.com/beagleboard/bb.org-overlays;\
	fi
	cp *.dts bb.org-overlays/src/arm
	make -C bb.org-overlays
	@for filename in $(shell ls *.dts); do\
		cp bb.org-overlays/src/arm/`basename "$${filename}" .dts`.dtbo .;\
	done

clean:
	rm *.dtbo
