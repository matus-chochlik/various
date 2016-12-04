#!/bin/bash
$(< $(dirname $0)/SOURCE_DIR)/gen_tex.sh \
	"${1}" \
	"$(< $(dirname $0)/YEAR)" \
	"$(< $(dirname $0)/LANGUAGE)" \
	"$(< $(dirname $0)/COUNTRY)" \
	"$(< $(dirname $0)/INPUT_DIR)"
