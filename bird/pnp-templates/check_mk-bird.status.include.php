<?php
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

$bird_prefix = strtok($this->MACRO['DISP_SERVICEDESC'], ' '); # Service description up to the first space (BIRD/BIRD6)

foreach($this->DS as $i => $ds)
{
    switch($ds['NAME']) {
        case 'uptime':
            $ds['DESC'] = "Uptime";
            $ds['UNIT'] = "days";
            $ds['COLOR_LINE'] = "#408000";
            $ds['COLOR_AREA'] = "#80f000";
            break;
        case 'time_since_last_reconfiguration':
            $ds['DESC'] = "Time since last reconfiguration";
            $ds['UNIT'] = "days";
            $ds['COLOR_LINE'] = "#005580";
            $ds['COLOR_AREA'] = "#00a0f0";
            break;
    }
    $opt[$i] = "--vertical-label '".$ds['UNIT']."' -l0 --title '".$this->MACRO['DISP_HOSTNAME']." / ".$bird_prefix." - ".$ds['DESC']."' ";

    $def[$i] = "";
    $def[$i] .= rrd::def('sec', $ds['RRDFILE'], $ds['DS'], 'MAX');
    $def[$i] .= rrd::cdef('days', 'sec,86400,/');
    $def[$i] .= rrd::area('days', $ds['COLOR_AREA'], rrd::cut($ds['DESC']." (".$ds['UNIT'].")", 40));
    $def[$i] .= rrd::line2('days', $ds['COLOR_LINE']);
    $def[$i] .= rrd::gprint('days', 'LAST', "%7.2lf %s LAST");
    $def[$i] .= rrd::gprint('days', 'MAX', "%7.2lf %s MAX");
}

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
