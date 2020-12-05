#!/bin/bash
# Copyright (c) 2020 Matus Chochlik
(
	locale | grep LANGUAGE | cut -d'=' -f2 | cut -d'_' -f1
	locale | sed -n 's/LC_\(NUMERIC\|TIME\|MESSAGES\)=\([a-z]\{2\}\)_[A-Z]\{2\}.*/\2/p'
) | grep "\S" | uniq | head -1
