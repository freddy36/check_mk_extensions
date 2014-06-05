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

$opt[1] = "-l 0 -b 1024 --title \"".str_replace("_", " ", $servicedesc)." Usage on $hostname\" ";

$colors = array("#00cc00","#0066b3","#ff8000","#ffcc00","#ccff00","#808080","#008f00","#00487d","#b35a00","#b38f00","#6b006b","#8fb300","#b30000");
$def[1] = "";

foreach ($RRDFILE as $i => $file) {
    $filename = basename($file);
    $fileprefixlength = strlen($servicedesc)+1;
    $key = substr($filename, $fileprefixlength, -4);
    $desc = str_replace("_", " ", $key);

    $def[1] .= "DEF:$key=$file:1:MAX ";
    if($key == "Total") {
        $def[1] .= "LINE:$key#000000:\"$desc".str_repeat(" ", 20 - strlen($desc))."\" ";
        if($WARN[$i] > 0)
            $def[1] .= "HRULE:$WARN[$i]#FFFF00 ";
        if($CRIT[$i] > 0)
            $def[1] .= "HRULE:$CRIT[$i]#FF0000 ";
    } else {
        $def[1] .= "AREA:$key$colors[$i]:\"$desc".str_repeat(" ", 20 - strlen($desc))."\":STACK ";
    }
    $def[1] .= "GPRINT:$key:LAST:\"%6.0lf %sB last\" ";
    $def[1] .= "GPRINT:$key:AVERAGE:\"%6.0lf %sB avg\" ";
    $def[1] .= "GPRINT:$key:MAX:\"%6.0lf %sB max\\n\" ";
}

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
