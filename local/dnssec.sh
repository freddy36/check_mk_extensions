#!/bin/bash

# A simple local check for check_mk to validate the DNSSEC trust chain using drill

# Install instructions:
# - Install drill:
#   apt-get install ldnsutils
# - Generate the trusted-key file for drill:
#   drill DNSKEY . | grep "257 "> /etc/trusted-key.key
# - Place this file in your agent's local check directory (/usr/lib/check_mk_agent/local)
# - Adjust the ZONES array below

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014 by Frederik Kriewitz <frederik@kriewitz.eu>.

# array with zones to check
#ZONES=("dnssec-failed.org")
ZONES=()
KEYFILE="/etc/trusted-key.key"

# add any local bind signed zones
for FILE in /var/cache/bind/*.zone.signed
do
	FILENAME=${FILE##*/}
	ZONE=${FILENAME%.zone.signed}
	ZONES+=($ZONE)
done

# check the zones
for ZONE in ${ZONES[@]}
do
	CHASE=$(drill -k "$KEYFILE" -TD $ZONE)
	RESULT_TEXT=$(echo "$CHASE" | awk '/^\[[^T]\]/' ORS=' ')
	if [ -n "$RESULT_TEXT" ];
	then
		STATUS=2
	else
		RESULT_TEXT=$(echo "$CHASE" | grep "^\[" | tail -n 1)
		STATUS=0
	fi

	echo  "$STATUS dnssec_$ZONE - ${RESULT_TEXT/;; /}"
done

