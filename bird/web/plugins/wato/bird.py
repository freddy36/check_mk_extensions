# -*- encoding: utf-8; py-indent-offset: 4 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

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

# bird.status
register_check_parameters(
    subgroup_applications,
    "bird_status",
    _("BIRD Status"),
    Dictionary(
        elements = [
            ("uptime_low_threshold",
                Integer(
                    title = _("Warning if uptime is lower than"),
                    unit = _("seconds"),
                    default_value = 300
                ),
            ),
            ("config_file_min_age",
                Integer(
                    title = _("Minimum config file age for last reconfiguration warnings:"),
                    unit = _("seconds"),
                    default_value = 60
                ),
            ),
	]
    ),
    None,
    "dict"
)

# bird.memory
bird_memory_valuespec = Dictionary(
    elements = [
        ( "memory_levels_Total",
            Tuple(
                title = _("Total memory usage"),
                elements = [
                    Integer(title = _("Warning if above"), unit = _("MB")),
                    Integer(title = _("Critical if above"), unit = _("MB")),
                ]
            ),
        )
    ]
)

# bird.protocols
bird_protocols_valuespec = Dictionary(
    elements = [
        ( "route_stats_levels",
            Dictionary(
                title = _("Route Statistics Levels"),
                elements = [
                    (i, Dictionary(
                        title = _(i),
                        elements = [
                            ("lower",
                                Tuple(
                                    help = _("Lower levels for the %s routes") % (i),
                                    title = _("Lower levels"),
                                    elements = [
                                        Integer(title = _("warning if below")),
                                        Integer(title = _("critical if below")),
                                    ]
                                ),
                            ),
                            ( "upper",
                                Tuple(
                                    help = _("Upper levels for the %s routes") % (i),
                                    title = _("Upper levels"),
                                    elements = [
                                        Integer(title = _("warning if above")),
                                        Integer(title = _("critical if above")),
                                    ]),
                            ),
                        ],
                        optional_keys = ["upper", "lower"],
                    )) for i in ["imported", "filtered", "exported", "preferred"]
            	]
            )
        ),
        ( "route_stats_levels_limit_warning_factor",
            Percentage(title = _("Warning level for limit based thresholds"), unit = _("percent"), default_value = 90, minvalue = 0, maxvalue = 100),
        )
    ]
)

bird_protocols_itemspec = TextAscii(
    title = _("Protocol"),
    allow_empty = False
)

# register memory/protocols parameters for each BIRD version
for bird_version in [ "", "6" ]:
    register_check_parameters(
        subgroup_applications,
        "bird%s_memory" % (bird_version),
        _("BIRD%s Memory" % (bird_version)),
        bird_memory_valuespec,
        None,
        "dict"
    )

    register_check_parameters(
        subgroup_applications,
        "bird%s_protocols" % (bird_version),
        _("BIRD%s Protocols" % (bird_version)),
        bird_protocols_valuespec,
        bird_protocols_itemspec,
        "dict"
)


