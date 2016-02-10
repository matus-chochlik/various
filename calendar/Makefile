# Copyright (c) 2015-2016 Matus Chochlik

YEAR = $(shell date +%Y)
BUILD_DIR = ./_build

all: $(BUILD_DIR)/foto-$(YEAR).pdf

$(BUILD_DIR)/%-$(YEAR).pdf: $(BUILD_DIR)/%-$(YEAR).tex
	cd $(BUILD_DIR) && pdflatex $*-$(YEAR).tex && cd ..

$(BUILD_DIR)/%-$(YEAR).tex: gen_tex.sh | $(BUILD_DIR)
	cd $(BUILD_DIR) && ../gen_tex.sh ../$* $(YEAR) > $*-$(YEAR).tex && cd ..

$(BUILD_DIR):
	mkdir -p $@

