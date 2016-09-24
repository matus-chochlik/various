all: \
	qiodevice.pdf \
	class_tree.pdf \
	qobject_tree.pdf \
	sig_slot_diag1.pdf \
	sig_slot_diag2.pdf \
	sig_slot_schema.pdf \
	anchors.pdf

%.pdf: %.svg
	inkscape --export-pdf $@ $<

%.svg: %.dot
	dot -Tsvg -o $@ $<

