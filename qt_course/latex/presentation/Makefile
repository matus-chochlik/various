include ../make.conf

OUTPDF = $(OUTDIR)/qt_course.pdf

all: $(OUTPDF)

.PHONY: clean
clean:
	rm -f $(OUTDIR)/*


$(OUTDIR)/%.pdf: ./%.tex | $(OUTDIR)
	pdflatex -shell-escape -output-directory=$(OUTDIR) $<

$(OUTDIR):
	mkdir -p $@
