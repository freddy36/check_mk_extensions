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

$route_change_stats_keys = array("Import_updates", "Import_withdraws", "Export_updates", "Export_withdraws");
$route_change_stats_fields = array(
    "rejected" => "#FF0000",
    "filtered" => "#E300B6",
    "ignored"  => "#E3DF00",
    "accepted" => "#00cc00",
    "received" => "#0066b3");
$scheme = array("#00cc00","#0066b3","#ff8000","#e7298a","#008f00","#00487d","#b35a00","#b38f00","#6b006b","#8fb300","#b30000");

$DS_BY_NAME = array();

foreach($this->DS as $i => &$ds)
{
    $ds['INDEX'] = $i;
    $DS_BY_NAME[$ds['NAME']] = $ds;
}

if(array_key_exists('since', $DS_BY_NAME))
{
    $ds = $DS_BY_NAME['since'];
    $ds['DESC'] = "Time since last state change";
    $ds['UNIT'] = "Days";
    $ds['COLOR_LINE'] = "#408000";
    $ds['COLOR_AREA'] = "#80f000";
    $i = $ds['INDEX'];
    $opt[$i] = "--vertical-label '".$ds['UNIT']."' -l0 --title '".$this->MACRO['DISP_HOSTNAME']." / ".$this->MACRO['DISP_SERVICEDESC']."' ";

    $def[$i] = "";
    $def[$i] .= rrd::def('sec', $ds['RRDFILE'], $ds['DS'], 'MAX');
    $def[$i] .= rrd::cdef('days', 'sec,86400,/');
    $def[$i] .= rrd::area('days', $ds['COLOR_AREA'], rrd::cut($ds['DESC']." (".$ds['UNIT'].")", 40));
    $def[$i] .= rrd::line2('days', $ds['COLOR_LINE']);
    $def[$i] .= rrd::gprint('days', 'LAST', "%7.2lf %s LAST");
    $def[$i] .= rrd::gprint('days', 'MAX', "%7.2lf %s MAX");
}

foreach($DS_BY_NAME as $name => $ds)
{
    if(strpos($name, 'route_stats_') === 0) {
        $ds['DESC'] = substr($ds['LABEL'], 12);
        $ds['COLOR_LINE'] = "#005580";
        $ds['COLOR_AREA'] = "#00a0f0";

        $i = $ds['INDEX'];

        $opt[$i] = "--vertical-label 'Routes' --title '".$this->MACRO['DISP_HOSTNAME']." / ".$this->MACRO['DISP_SERVICEDESC']."' ";

        $def[$i] = "";
        $def[$i] .= rrd::def($ds['NAME'], $ds['RRDFILE'], $ds['DS'], 'MAX');
        $def[$i] .= rrd::area($ds['NAME'], $ds['COLOR_AREA'], rrd::cut($ds['DESC'], 30), True);
        $def[$i] .= rrd::line2($ds['NAME'], $ds['COLOR_LINE']);
        foreach(array("WARN" => "#FFFF00", "CRIT" => "#FF0000") as $type => $color) {
            foreach(array("MIN", "MAX") as $level) {
                $limit_key = $type."_".$level;
                $limit_value = $ds[$limit_key];
                if(is_numeric($limit_value) && $limit_value > 0) {
                    $def[$i] .= rrd::hrule($limit_value, $color);
                }
            }
        }
        $def[$i] .= rrd::gprint($ds['NAME'], 'LAST', "%7.0lf LAST");
        $def[$i] .= rrd::gprint($ds['NAME'], 'MIN', "%7.0lf MIN");
        $def[$i] .= rrd::gprint($ds['NAME'], 'MAX', "%7.0lf MAX");
    }

}

if(array_key_exists('neighbours', $DS_BY_NAME)) {
    $ds = $DS_BY_NAME['neighbours'];
    $ds['DESC'] = "Neighbours";
    $ds['COLOR_LINE'] = "#806B00";
    $ds['COLOR_AREA'] = "#f0c800";

    $i = 90;

    $opt[$i] = "--vertical-label 'Neighbours' -l0 --title '".$this->MACRO['DISP_HOSTNAME']." / ".$this->MACRO['DISP_SERVICEDESC']."' ";

    $def[$i] = "";
    $def[$i] .= rrd::def($ds['NAME'], $ds['RRDFILE'], $ds['DS'], 'MAX');
    $def[$i] .= rrd::area($ds['NAME'], $ds['COLOR_AREA'], rrd::cut($ds['DESC'], 30));
    $def[$i] .= rrd::line2($ds['NAME'], $ds['COLOR_LINE']);
    $def[$i] .= rrd::gprint($ds['NAME'], 'LAST', "%7.0lf LAST");
    $def[$i] .= rrd::gprint($ds['NAME'], 'MIN', "%7.0lf MIN");
    $def[$i] .= rrd::gprint($ds['NAME'], 'MAX', "%7.0lf MAX");
}

$i = 100;
foreach($route_change_stats_keys as $key) {
    foreach($route_change_stats_fields as $field => $color) {
        $ds_key = "route_change_stats_".$key."_".$field;
        if(!array_key_exists($ds_key, $DS_BY_NAME))
            continue;

        $ds = $DS_BY_NAME[$ds_key];
        $ds['DESC'] = str_replace("_", " ", $key)." ".$field;
        $ds['COLOR'] = $color;

        if(!array_key_exists($i, $opt)) {
            $opt[$i] = "--vertical-label 'Events per second' -l0 --title '".$this->MACRO['DISP_HOSTNAME']." / ".$this->MACRO['DISP_SERVICEDESC']."' ";
            $def[$i] = "";
        }

        $def[$i] .= rrd::def($ds['NAME'], $ds['RRDFILE'], $ds['DS'], 'MAX');
        if($field == "received") {
            $def[$i] .= rrd::line2($ds['NAME'], $ds['COLOR'], rrd::cut($ds['DESC'], 30), False);
        } else {
            $def[$i] .= rrd::area($ds['NAME'], $ds['COLOR'], rrd::cut($ds['DESC'], 30), True);
        }
        $def[$i] .= rrd::gprint($ds['NAME'], 'LAST', "%7.2lf LAST");
        $def[$i] .= rrd::gprint($ds['NAME'], 'MIN', "%7.2lf MIN");
        $def[$i] .= rrd::gprint($ds['NAME'], 'MAX', "%7.2lf MAX");
    }
    $i++;
}

# vim: set filetype=php expandtab tabstop=8 shiftwidth=4 softtabstop=4 autoindent smartindent
?>

