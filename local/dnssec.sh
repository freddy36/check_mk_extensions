#!/bin/bash

# A simple local check for check_mk to validate the DNSSEC trust chain using the dig +sigchase feature

# Install instructions:
# - Install dig:
#   apt-get install dnsutils
# - Generate the trusted-key file for dig:
#   dig . dnskey | grep 257 > /etc/trusted-key.key
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
ZONES=()

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
	CHASE=$(dig +topdown +sigchase $ZONE)
	RESULT_TEXT=$(echo "$CHASE" | grep "^\;\;" | grep -Fv 'cleanandgo' | tail -n 1)
	RESULT=$(echo "$RESULT_TEXT" | awk '{print $NF}')

	if [ "$RESULT" == "SUCCESS" ];
	then
		STATUS=0
	elif [ "$RESULT" == "FAILED" ];
	then
		STATUS=2
	else
		STATUS=3
	fi

	echo  "$STATUS dnssec_$ZONE - ${RESULT_TEXT/;; /}"
done

