# Copyright (c) 2015-2016 Matus Chochlik

BUILD_DIR = ./_build

all: $(BUILD_DIR)/foto.pdf

$(BUILD_DIR)/%.pdf: $(BUILD_DIR)/%.tex
	cd $(BUILD_DIR) && pdflatex $*.tex && cd ..

$(BUILD_DIR)/%.tex: $(BUILD_DIR)/call_gen_tex.sh | $(BUILD_DIR)
	cd $(BUILD_DIR) && ./call_gen_tex.sh "$*" > $*.tex && cd ..

$(BUILD_DIR)/call_gen_tex.sh: call_gen_tex.sh \
	$(BUILD_DIR)/SOURCE_DIR \
	$(BUILD_DIR)/YEAR \
	$(BUILD_DIR)/LANGUAGE \
	$(BUILD_DIR)/COUNTRY \
	$(BUILD_DIR)/INPUT_DIR
	cp $< $@

$(BUILD_DIR)/SOURCE_DIR $(BUILD_DIR)/INPUT_DIR: | $(BUILD_DIR)
	pwd > $@

$(BUILD_DIR)/YEAR: | $(BUILD_DIR)
	date +%Y > $@

$(BUILD_DIR)/LANGUAGE: | $(BUILD_DIR)
	locale | grep LANGUAGE | cut -d'=' -f2 | cut -d'_' -f1 > $@

$(BUILD_DIR)/COUNTRY: | $(BUILD_DIR)
	locale | grep LANGUAGE | cut -d'=' -f2 | cut -d'_' -f2 > $@

$(BUILD_DIR):
	mkdir -p $@

