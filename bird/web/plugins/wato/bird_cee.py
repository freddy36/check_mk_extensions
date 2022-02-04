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

try:
    from cmk.gui.i18n import _
    from cmk.gui.plugins.wato import (
        HostRulespec,
        rulespec_registry,
    )
    from cmk.gui.cee.plugins.wato.agent_bakery.rulespecs.utils import RulespecGroupMonitoringAgentsAgentPlugins
    from cmk.gui.valuespec import (
        DropdownChoice,
    )
    
    def _valuespec_agent_config_bird():
        return DropdownChoice(
            title = _("BIRD Internet Routing Daemon (Linux)"),
            help = _("This will deploy the agent plugin <tt>bird</tt> for checking the BIRD Internet Routing Daemon."),
            choices = [
                ( True, _("Deploy plugin for BIRD") ),
                ( None, _("Do not deploy plugin for BIRD") ),
            ]
        )
    
    rulespec_registry.register(
        HostRulespec(
            group=RulespecGroupMonitoringAgentsAgentPlugins,
            name="agent_config:bird",
            valuespec=_valuespec_agent_config_bird,
        ))

except ModuleNotFoundError:
    # RAW edition
    pass
