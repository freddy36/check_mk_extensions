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

$opt[1] = "-l 0 -b 1024 --title '".$this->MACRO['DISP_HOSTNAME']." / ".$bird_prefix." - Memory usage' ";

$scheme = array("#00cc00","#0066b3","#ff8000","#e7298a","#008f00","#00487d","#b35a00","#b38f00","#6b006b","#8fb300","#b30000");

$def[1] = "";
foreach($this->DS as $i => $ds)
{
    $ds['DESC'] = str_replace("_", " ", $ds['LABEL']);

    $def[1] .= rrd::def($ds['NAME'], $ds['RRDFILE'], $ds['DS'], 'MAX');
    if($ds['NAME'] == "Total") {
    if($ds['WARN'] > 0 && $ds['CRIT'] > 0) {
        $def[1] .= rrd::hrule($ds['WARN'], "#FFFF00");
        $def[1] .= rrd::hrule($ds['CRIT'], "#FF0000");
        $def[1] .= rrd::ticker($ds['NAME'], $ds['WARN'], $ds['CRIT'], -0.01);
    }
        $def[1] .= rrd::line1($ds['NAME'], '#000000', rrd::cut($ds['DESC'], 20));
    } else {
        $def[1] .= rrd::area($ds['NAME'], rrd::color($i, '', $scheme), rrd::cut($ds['DESC'], 20), True);
    }
    $def[1] .= rrd::gprint($ds['NAME'], 'LAST', "%6.0lf %sB LAST");
    $def[1] .= rrd::gprint($ds['NAME'], 'AVERAGE', "%6.0lf %sB AVG");
    $def[1] .= rrd::gprint($ds['NAME'], 'MAX', "%6.0lf %sB MAX");
}

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
?>
