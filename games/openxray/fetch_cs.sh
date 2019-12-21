#!/bin/bash
steamcmd "\
	+@sSteamCmdForcePlatformType windows" \
	+login "${STEAMUSER:-${USER}}" \
	+force_install_dir "$(realpath $(dirname ${0})/resources/GSC/SCS/)" \
	+app_update 20510 \
	+quit
