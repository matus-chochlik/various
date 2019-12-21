#!/bin/bash
steamcmd "\
	+@sSteamCmdForcePlatformType windows" \
	+login "${STEAMUSER:-${USER}}" \
	+force_install_dir "$(realpath $(dirname ${0})/resources/GSC/SCOP/)" \
	+app_update 41700 \
	+quit
