TMP=/tmp/atmost_presentation

all: presentation.pdf

%.pdf: $(TMP)/%.pdf
	cp $< $@

$(TMP)/%.pdf: $(TMP)/%.tex
	pdflatex -shell-escape -output-directory=$(TMP) $<

$(TMP)/presentation.pdf: \
	$(TMP)/resusage-llvm-16GB-ld-noccache-1j.pdf \
	$(TMP)/resusage-llvm-16GB-ld-noccache-2j.pdf \
	$(TMP)/resusage-llvm-16GB-ld-noccache-3j.pdf \
	$(TMP)/resusage-llvm-16GB-ld-noccache-7j.pdf \
	$(TMP)/reboot-llvm-16GB-ld-noccache-9j.pdf \
	$(TMP)/resusage-llvm-16GB-gold-ccache-12j.pdf \
	$(TMP)/time-llvm-16GB-ld-noccache-vs-ccache-1j.pdf \
	$(TMP)/scatter-llvm-buildtime-ramusage-ccache-8G-8C.pdf \
	$(TMP)/scatter-llvm-buildtime-ramusage-noccache-8G-8C.pdf \
	$(TMP)/hist-llvm-link-mem-req.pdf

$(TMP)/%.tex: %.tex
	cp $< $@

$(TMP)/resusage-llvm-16GB-ld-noccache-%j.pdf: \
	data/llvm.ld.16GB.nozram.noccache.%.json.gz \
	tools/plot-link-res-usage.py | $(TMP)
	tools/plot-link-res-usage.py \
		-i data/llvm.ld.16GB.nozram.noccache.$*.json.gz  \
		-o $@

$(TMP)/resusage-llvm-16GB-gold-ccache-%j.pdf: \
	data/llvm.gold.16GB.zram.ccache.%.json.gz \
	tools/plot-link-res-usage.py | $(TMP)
	tools/plot-link-res-usage.py \
		-i data/llvm.gold.16GB.zram.ccache.$*.json.gz  \
		-o $@

$(TMP)/reboot-llvm-16GB-ld-noccache-%j.pdf: \
	data/llvm.ld.16GB.nozram.noccache.%.json.gz \
	tools/plot-link-res-usage-crash.py | $(TMP)
	tools/plot-link-res-usage-crash.py \
		-i data/llvm.ld.16GB.nozram.noccache.$*.json.gz  \
		-o $@

$(TMP)/time-llvm-16GB-ld-noccache-vs-ccache-%j.pdf: \
	data/llvm-gold-distcc-ccache-8G-8C.json.gz \
	data/llvm-gold-distcc-noccache-8G-8C.json.gz \
	tools/plot-link-slow-fast.py | $(TMP)
	tools/plot-link-slow-fast.py \
		-f data/llvm-gold-distcc-ccache-8G-8C.json.gz \
		-F "ccached with 100% hit rate" \
		-s data/llvm-gold-distcc-noccache-8G-8C.json.gz \
		-S "clean build without ccache" \
		-j $* \
		-o $@

$(TMP)/scatter-llvm-buildtime-ramusage-%-8G-8C.pdf: \
	data/llvm-gold-distcc-%-8G-8C.json.gz \
	tools/plot-link-time-ram-usage.py | $(TMP)
	tools/plot-link-time-ram-usage.py \
		-i data/llvm-gold-distcc-$*-8G-8C.json.gz \
		-j 1 \
		-o $@

$(TMP)/hist-llvm-link-mem-req.pdf: \
	data/llvm-gold-distcc-ccache-8G-8C.json.gz \
	data/llvm-gold-distcc-noccache-8G-8C.json.gz \
	data/llvm-gold-distcc-ccache-8G-8C-7J.json.gz \
	tools/plot-link-mem-req-hist.py | $(TMP)
	tools/plot-link-mem-req-hist.py \
		-i data/llvm-gold-distcc-ccache-8G-8C.json.gz \
		-i data/llvm-gold-distcc-noccache-8G-8C.json.gz \
		-i data/llvm-gold-distcc-ccache-8G-8C-7J.json.gz \
		-o $@

$(TMP):
	mkdir -p $@

.PHONY: clean
clean:
	rm -rf $(TMP)/*
