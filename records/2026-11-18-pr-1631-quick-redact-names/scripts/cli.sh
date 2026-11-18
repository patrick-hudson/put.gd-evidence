#!/bin/bash
# cli.sh METHOD [JSON]  — runs putgd-cli against the private resident
R=/run/user/$(id -u)/qr
export XDG_RUNTIME_DIR=$R
exec /usr/bin/putgd-cli "$@"
