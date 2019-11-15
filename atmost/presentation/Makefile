TMP=/tmp/atmost_presentation

all: presentation.pdf

%.pdf: $(TMP)/%.pdf
	cp $< $@

$(TMP)/%.pdf: $(TMP)/%.tex
	pdflatex -shell-escape -output-directory=$(TMP) $< &&\
	pdflatex -shell-escape -output-directory=$(TMP) $<

$(TMP)/presentation.pdf: \
	$(TMP)/resusage-llvm-16GB-ld-noccache-1j.pdf \
	$(TMP)/resusage-llvm-16GB-ld-noccache-2j.pdf \
	$(TMP)/resusage-llvm-16GB-ld-noccache-3j.pdf \
	$(TMP)/resusage-llvm-16GB-ld-noccache-7j.pdf \
	$(TMP)/reboot-llvm-16GB-ld-noccache-9j.pdf \
	$(TMP)/resusage-llvm-16GB-gold-ccache-12j.pdf \
	$(TMP)/time-llvm-8GB-ld-noccache-vs-ccache-1j.pdf \
	$(TMP)/time-llvm-16GB-ld-noccache-1j-16j.pdf \
	$(TMP)/time-llvm-8GB-ld-noccache-1j-16j.pdf \
	$(TMP)/time-llvm-8GB-ld-ccache-1j-16j.pdf \
	$(TMP)/scatter-llvm-buildtime-ramusage-ccache-8G-8C.pdf \
	$(TMP)/scatter-llvm-buildtime-ramusage-noccache-8G-8C.pdf \
	$(TMP)/hist-llvm-link-mem-req.pdf \
	$(TMP)/prediction-actual-vs-predicted.pdf \
	$(TMP)/gantt-noccache-16G-10j.pdf \
	$(TMP)/gantt-noccache-16G-20j.pdf \
	$(TMP)/gantt-noccache-8G-10j.pdf \
	$(TMP)/gantt-noccache-8G-20j.pdf \
	$(TMP)/gantt-ccache-8G-20j.pdf \
	$(TMP)/stats-llvm-noccache-16G-4C.pdf \
	$(TMP)/stats-llvm-noccache-8G-8C.pdf \
	$(TMP)/stats-llvm-ccache-8G-8C.pdf \
	$(TMP)/stats-oglplus-tidy-8C.pdf \
	$(TMP)/diagram-components.pdf

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

$(TMP)/time-llvm-8GB-ld-noccache-vs-ccache-%j.pdf: \
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

$(TMP)/time-llvm-16GB-ld-noccache-1j-%j.pdf: \
	data/llvm-gold-distcc-noccache-16G-4C.json.gz \
	tools/plot-link-finish-j.py | $(TMP)
	tools/plot-link-finish-j.py \
		-i data/llvm-gold-distcc-noccache-16G-4C.json.gz \
		-j 1 \
		-j $* \
		-o $@

$(TMP)/time-llvm-8GB-ld-noccache-1j-%j.pdf: \
	data/llvm-gold-distcc-noccache-8G-8C.json.gz \
	tools/plot-link-finish-j.py | $(TMP)
	tools/plot-link-finish-j.py \
		-i data/llvm-gold-distcc-noccache-8G-8C.json.gz \
		-j 1 \
		-j $* \
		-o $@

$(TMP)/time-llvm-8GB-ld-ccache-1j-%j.pdf: \
	data/llvm-gold-distcc-ccache-8G-8C.json.gz \
	tools/plot-link-finish-j.py | $(TMP)
	tools/plot-link-finish-j.py \
		-i data/llvm-gold-distcc-ccache-8G-8C.json.gz \
		-j 1 \
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

$(TMP)/prediction-actual-vs-predicted.pdf: \
	data/llvm-gold-distcc-ccache-8G-8C.json.gz \
	data/llvm-gold-distcc-noccache-8G-8C.json.gz \
	data/llvm-gold-distcc-ccache-8G-8C-7J.json.gz \
	tools/plot-link-actu-pred.py | $(TMP)
	tools/plot-link-actu-pred.py \
		-i data/llvm-gold-distcc-ccache-8G-8C.json.gz \
		-i data/llvm-gold-distcc-noccache-8G-8C.json.gz \
		-i data/llvm-gold-distcc-ccache-8G-8C-7J.json.gz \
		-o $@

$(TMP)/gantt-noccache-16G-%j.pdf: \
	data/llvm-gold-distcc-noccache-16G-4C.json.gz \
	tools/plot-link-gantt.py | $(TMP)
	tools/plot-link-gantt.py \
		-i data/llvm-gold-distcc-noccache-16G-4C.json.gz \
		-j $* \
		-o $@

$(TMP)/gantt-noccache-8G-%j.pdf: \
	data/llvm-gold-distcc-noccache-8G-8C.json.gz \
	tools/plot-link-gantt.py | $(TMP)
	tools/plot-link-gantt.py \
		-i data/llvm-gold-distcc-noccache-8G-8C.json.gz \
		-j $* \
		-o $@

$(TMP)/gantt-ccache-8G-%j.pdf: \
	data/llvm-gold-distcc-ccache-8G-8C.json.gz \
	tools/plot-link-gantt.py | $(TMP)
	tools/plot-link-gantt.py \
		-i data/llvm-gold-distcc-ccache-8G-8C.json.gz \
		-j $* \
		-o $@

$(TMP)/stats-llvm-%-16G-4C.pdf: \
	data/llvm-gold-distcc-%-16G-4C.json.gz \
	tools/plot-link-spdp-effi.py | $(TMP)
	tools/plot-link-spdp-effi.py \
		-i data/llvm-gold-distcc-$*-16G-4C.json.gz \
		-o $@

$(TMP)/stats-llvm-%-8G-8C.pdf: \
	data/llvm-gold-distcc-%-8G-8C.json.gz \
	tools/plot-link-spdp-effi.py | $(TMP)
	tools/plot-link-spdp-effi.py \
		-i data/llvm-gold-distcc-$*-8G-8C.json.gz \
		-o $@

$(TMP)/stats-oglplus-tidy-8C.pdf: \
	data/oglplus-clang-tidy-8C-times.json \
	tools/plot-tidy-spdp-effi.py | $(TMP)
	tools/plot-tidy-spdp-effi.py \
		-i data/oglplus-clang-tidy-8C-times.json \
		-o $@

$(TMP)/diagram-%.pdf: images/%.dot
	dot -Gnewrank -Tpdf -o $@ $<

$(TMP):
	mkdir -p $@

.PHONY: clean
clean:
	rm -rf $(TMP)/*
