TEMPLATE = subdirs
CONFIG += ordered

SUBDIRS += \
	01_hv_layouts/layout.pro \
	02_form_layout/layout.pro \
	03_grid_layout/layout.pro \
	04_stack_layout/layout.pro \
	05_sigslot_intro/sigslot.pro \
	06_sigslot_reverse/sigslot.pro \
	06_core_app/core_app.pro \
	07_clarg_parser/arg_parse.pro \
	08_settings/settings.pro \
	10_resources/resources.pro \
	11_http_request/http_req.pro
