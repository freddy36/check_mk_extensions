#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# This file is part of the check_mk bird check.
#
# The check_mk bird check is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The check_mk bird check is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with it. If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014 by Frederik Kriewitz <frederik@kriewitz.eu>.

from cmk.gui.views.perfometer.legacy_perfometers.check_mk import perfometer_check_mk_uptime
from cmk.gui.views.perfometer.legacy_perfometers.utils import perfometer_logarithmic

perfometers["check_mk-bird_status"]      = perfometer_check_mk_uptime
perfometers["check_mk-bird6_status"]     = perfometer_check_mk_uptime

def perfometer_check_mk_bird_protocols(row, check_command, perf_data):
    value = list(filter(lambda x: x.metric_name == "route_stats_imported", perf_data))[0].value
    return "%d imported" % value, perfometer_logarithmic(value, 20000 , 2 , "#da6")

perfometers["check_mk-bird_protocols"]   = perfometer_check_mk_bird_protocols
perfometers["check_mk-bird6_protocols"]  = perfometer_check_mk_bird_protocols

def perfometer_check_mk_bird_memory(row, check_command, perf_data):
    value = list(filter(lambda x: x.metric_name == "Total", perf_data))[0].value
    value_mb = value/1024/1024
    return "%d MB" % value_mb, perfometer_logarithmic(value_mb, 500 , 2 , "#80ff40")

perfometers["check_mk-bird_memory"]   = perfometer_check_mk_bird_memory
perfometers["check_mk-bird6_memory"]  = perfometer_check_mk_bird_memory

