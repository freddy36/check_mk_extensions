#!/usr/bin/env python3
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

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Integer,
    Filesize,
    Tuple,
)

from cmk.gui.plugins.wato import (
    rulespec_registry,
    CheckParameterRulespecWithoutItem,
    CheckParameterRulespecWithItem,
    RulespecGroupCheckParametersApplications,
)

# bird.status
def _parameter_valuespec_bird_status():
    return Dictionary(
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
        ],
        ignored_keys = ['config_files', 'memory', 'protocols', 'status', 'version'],
    )

rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="bird_status",
        group=RulespecGroupCheckParametersApplications,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_bird_status,
        title=lambda: _("BIRD Status"),
    ))


# bird.memory
def _parameter_valuespec_bird_memory():
    return Dictionary(
        elements = [
            ( "memory_levels_Total",
              Tuple(
                  title = _("Total memory usage"),
                  elements = [
                      Filesize(title = _("Warning if above")),
                      Filesize(title = _("Critical if above")),
                  ]
              ),
            )
        ],
        ignored_keys = ['config_files', 'memory', 'protocols', 'status', 'version'],
    )

# bird.protocols
def _parameter_valuespec_bird_protocols():
    return Dictionary(
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
        ],
        ignored_keys = ['config_files', 'memory', 'protocols', 'status', 'version'],
    )

def _item_spec_bird_protocols():
    return TextAscii(
        title = _("Protocol"),
        allow_empty = False
    )

# register memory/protocols parameters for each BIRD version
for bird_version in [ "", "6" ]:
    rulespec_registry.register(
        CheckParameterRulespecWithoutItem(
            check_group_name="bird%s_memory" % bird_version,
            group=RulespecGroupCheckParametersApplications,
            match_type="dict",
            parameter_valuespec=_parameter_valuespec_bird_memory,
            title=lambda: _("BIRD%s Memory" % bird_version),
        ))

    rulespec_registry.register(
        CheckParameterRulespecWithItem(
            check_group_name="bird%s_protocols" % bird_version,
            group=RulespecGroupCheckParametersApplications,
            item_spec=_item_spec_bird_protocols,
            match_type="dict",
            parameter_valuespec=_parameter_valuespec_bird_protocols,
            title=lambda: _("BIRD%s Protocols" % bird_version),
        ))
