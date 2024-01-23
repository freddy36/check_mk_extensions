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
#
# ported to CMK 2.0 2021 by Robert Sander <r.sander@heinlein-support.de>

# Example data from agent:
# <<<bird>>>
# 0001 BIRD 1.4.3 ready.
# 1000 BIRD 1.4.3
# 1011 Router ID is 192.0.2.125
# 1011     Current server time is 2014-06-05 16:26:52
# 1011     Last reboot on 2014-06-02 17:15:23
# 1011     Last reconfiguration on 2014-06-03 14:37:54
# 0013 Daemon is up and running
# 1018 BIRD memory usage
# 1018     Routing tables:    137 MB
# 1018     Route attributes:   73 MB
# 1018     ROA tables:        192  B
# 1018     Protocols:        1697 kB
# 1018     Total:             211 MB
# 2002 name     proto    table    state  since       info
# 1002 o_test   OSPF     t_o_test up     2014-06-02 17:15:23  Running
# 1006   Preference:     150
# 1006       Input filter:   ACCEPT
# 1006       Output filter:  (unnamed)
# 1006       Routes:         421 imported, 458 exported, 1260 preferred
# 1006       Route change stats:     received   rejected   filtered    ignored   accepted
# 1006         Import updates:            469          0          0          0        469
# 1006         Import withdraws:            9          0        ---          0          9
# 1006         Export updates:            933        468          0        ---        465
# 1006         Export withdraws:           15        ---        ---        ---          7
# 1006
# 1002 b_error_test BGP      t_b_test start  2014-06-02 17:15:23  Connect       Socket: Network is unreachable
# 1006   Preference:     100
# 1006       Input filter:   REJECT
# 1006       Output filter:  ACCEPT
# 1006       Routes:         0 imported, 0 exported, 0 preferred
# 1006       Route change stats:     received   rejected   filtered    ignored   accepted
# 1006         Import updates:              0          0          0          0          0
# 1006         Import withdraws:            0          0        ---          0          0
# 1006         Export updates:              0          0          0        ---          0
# 1006         Export withdraws:            0        ---        ---        ---          0
# 1006       BGP state:          Connect
# 1006         Neighbor address: 192.0.2.6
# 1006         Neighbor AS:      65535
# 1006         Last error:       Socket: Network is unreachable
# 1006
# 1002 b_spamhouse1 BGP      t_b_blackhole up     2014-06-02 17:23:02  Established
# 1006   Description:    blackhole from spamhouse
# 1006   Preference:     40000
# 1006       Input filter:   b_spamhouse_in
# 1006       Output filter:  REJECT
# 1006       Import limit:   2000
# 1006         Action:       restart
# 1006       Routes:         1102 imported, 0 filtered, 0 exported, 3306 preferred
# 1006       Route change stats:     received   rejected   filtered    ignored   accepted
# 1006         Import updates:           1102          0          0          0       1102
# 1006         Import withdraws:            0          0        ---          0          0
# 1006         Export updates:           1105       1105          0        ---          0
# 1006         Export withdraws:            2        ---        ---        ---          0
# 1006       BGP state:          Established
# 1006         Neighbor address: 94.228.136.140
# 1006         Neighbor AS:      65190
# 1006         Neighbor ID:      94.228.136.140
# 1006         Neighbor caps:    refresh AS4
# 1006         Session:          external multihop AS4
# 1006         Source address:   192.0.2.125
# 1006         Route limit:      1102/2000
# 1006         Hold timer:       117/180
# 1006         Keepalive timer:  25/60
# 1006
# 1013 o_test:
# 1013     Router ID      Pri          State      DTime   Interface  Router IP
# 1013     192.0.2.126          1         full/bdr    00:08   vlan811    192.0.2.126
# 10000 1401799073 /etc/bird/bird.conf
# 10000 1401204399 /etc/bird/bird.conf.common
# 10000 1399909638 /etc/bird/bird.conf.local

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import (
    check_levels,
    get_rate,
    get_value_store,
    register,
    render,
    Result,
    Metric,
    State,
    Service,
    )

import time
import datetime

_bird_status_default_levels = {
    "uptime_low_threshold": 300,
    "config_file_min_age": 60,
}

_bird_protocols_default_levels = {
    "route_stats_levels_limit_warning_factor": 90.0,
}

def _bird_strptime(string):
    # bird uses different time formats depending on the version/settings
    for f in ['%d-%m-%Y %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S.%f', '%d-%m-%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S']:
        try:
            return datetime.datetime.strptime(string, f)
        except ValueError:
            pass
    raise ValueError("no timeformat matched %s" % (string))

def _bird_si_to_int(value, unit):
    _prefix = {'': 1, 'k': 1024, 'M': 1048576, 'G': 1073741824}
    return int(float(value) * _prefix[unit.rstrip('B')])

def _bird_x_to_key(value):
    return "_".join(value).rstrip(':')

def parse_bird(string_table):
    section = {}
    last_protocol = None
    for line in string_table:
        code = int(line[0])
        if 8000 <= code <= 9999:
            section['error'] = " ".join(line[1:])
        if code == 1000:
            section['version'] = line[2]
        elif code == 1011:
            if 'status' not in section:
                section['status'] = {}
            status = section.setdefault('status', {})
            if line[1] == 'Router' and line[2] == 'ID':
                status['router_id'] = line[4]
            elif line[1] == 'Current' and line[2] == 'server' and line[3] == 'time':
                status['server_time'] = " ".join(line[5:7])
            elif line[1] == 'Last' and line[2] == 'reboot':
                status['last_reboot'] = " ".join(line[4:6])
            elif line[1] == 'Last' and line[2] == 'reconfiguration':
                status['last_reconfiguration'] = " ".join(line[4:6])
        elif code == 24:
            graceful_restart_recovery_msgs = section['status'].setdefault('graceful_restart_recovery_msgs', [])
            graceful_restart_recovery_msgs.append(" ".join(line[1:]))
        elif code == 13:
            if 'status' not in section:
                section['status'] = {}
            section['status']['msg'] = " ".join(line[1:])
        elif code == 1018:
            if line[-1][-1] == 'B': # ignore lines which don't end vith B (not memory stats)
                memory = section.setdefault('memory', [])
                split_index = next(filter(lambda i: ':' in line[i], range(1, len(line))))
                name = " ".join(line[1:split_index+1]).rstrip(":")
                if split_index == len(line) - 5:
                    value_text = "E={} {}; O={} {}".format(*line[-4:])
                    value_bytes = _bird_si_to_int(line[-4], line[-3]) + _bird_si_to_int(line[-2], line[-1])
                else:
                    value_text = " ".join(line[split_index+1:])
                    value_bytes = _bird_si_to_int(line[-2], line[-1])
                memory.append((name, value_text, value_bytes))
        elif code == 1002:
            protocols = section.setdefault('protocols', {})
            last_protocol = protocols[line[1]] = {'proto': line[2], 'table': line[3], 'state': line[4]}
            try:
                # try to get absolute time (works in case "timeformat protocol iso long;" is configured)
                last_protocol['since'] = " ".join(line[5:7])
                last_protocol['info'] = " ".join(line[7:])
            except ValueError:
                last_protocol['since'] = line[5]
                last_protocol['info'] = " ".join(line[6:])
        elif code == 1006:
            if len(line) == 1:
                continue
            if line[1] == "Description:":
                last_protocol['description'] = " ".join(line[2:])
            if line[1] == "Preference:":
                last_protocol['preference'] = line[2]
            elif len(line) >= 3 and line[2] == "filter:":
                key = _bird_x_to_key(line[1:3])
                last_protocol[key] = " ".join(line[3:])
            elif len(line) >= 3 and line[2] == "limit:" and line[1] != 'Route':
                limits = last_protocol.setdefault('limits', {})
                last_limit = limits[line[1]] = {}
                last_limit['value'] = int(line[3])
                last_limit['hit'] = (len(line) >= 5 and line[4] == "[HIT]")
            elif line[1] == "Action:":
                last_limit['action'] = line[2]
            elif len(line) >= 3 and line[2] == "limit:" and line[1] == 'Route': # legacy "route limit" option
                limits = last_protocol.setdefault('limits', {})
                if 'Import' in limits:
                    continue # ignore in case we already have a import limit
                last_limit = limits['Import'] = {}
                last_limit['value'] = int(line[3].split("/")[1])
                last_limit['hit'] = False
                last_limit['action'] = "restart"
            elif line[1] == "Routes:":
                route_stats = last_protocol['route_stats'] = {}
                for i in range(2,len(line),2):
                    route_stats[line[i+1].rstrip(",")] = int(line[i])
            elif line[1] == "Route" and line[2] == "change" and line[3] == "stats:":
                route_change_stats_fields = line[4:]
                route_change_stats = last_protocol['route_change_stats'] = {}
            elif line[1] in ('Import', 'Export') and line[2] in ('updates:', 'withdraws:'):
                key = _bird_x_to_key(line[1:3])
                route_change_stats[key] = []
                for field, value in zip(route_change_stats_fields, line[3:]):
                    if value == "---":
                        value = None
                    else:
                        value = int(value)
                    route_change_stats[key].append((field, value))
        elif code == 1013:
            if line[1][-1] == ":":
                last_protocol = protocols[line[1][:-1]]
                last_protocol['neighbours'] = []
            elif len(line) == 7: # neighbours
                neighbour = {}
                for field, value in zip(['Router_ID', 'Pri', 'State', 'DTime', 'Interface', 'Router_IP'], line[1:]):
                    neighbour[field] = value
                last_protocol['neighbours'].append(neighbour)
        elif code == 10000:
            section.setdefault('config_files', []).append((" ".join(line[2:]), int(line[1])))

    return section

register.agent_section(
    name="bird",
    parse_function=parse_bird,
)

register.agent_section(
    name="bird6",
    parse_function=parse_bird,
)

def discover_bird_status(section) -> DiscoveryResult:
    if 'status' in section: # bird is running
        yield Service()

def check_bird_status(params, section) -> CheckResult:
    if 'error' in section:
        yield Result(state=State.CRIT,
                     summary="ERROR: "+section['error'])
        return
    if 'status' not in section:
        yield Result(state=State.UNKNOWN,
                     summary="No status information available")
        return
    status = section['status']
    if 'msg' not in status:
        yield Result(state=State.UNKNOWN,
                     summary="No status message available")
        return

    uptime = _bird_strptime(status['server_time']) - _bird_strptime(status['last_reboot'])
    time_since_last_reconfiguration = _bird_strptime(status['server_time']) - _bird_strptime(status['last_reconfiguration'])
    yield Metric('uptime', uptime.total_seconds())
    yield Metric('time_since_last_reconfiguration', time_since_last_reconfiguration.total_seconds())
    yield Result(state=State.OK,
                 summary="version %s" % section['version'])
    if status['msg'] == "Shutdown in progress":
        yield Result(state=State.CRIT,
                     summary=status['msg'])
    elif 'graceful_restart_recovery_msgs' in status:
        yield Result(state=State.WARN,
                     summary=status['graceful_restart_recovery_msgs'])
    elif status['msg'] == "Reconfiguration in progress":
        yield Result(state=State.WARN,
                     summary=status['msg'])
    elif status['msg'] == "Daemon is up and running":
        state = State.OK
        if uptime < datetime.timedelta(seconds=params['uptime_low_threshold']):
            state = State.WARN
        yield Result(state=state,
                     summary="up since %s" % (str(uptime).replace(",", " and")))
        yield Result(state=State.OK,
                     summary="last reconfiguration: %s" % _bird_strptime(status['last_reconfiguration']))
        for config_file, mtimestamp in section.get('config_files', []):
            mtime = datetime.datetime.fromtimestamp(mtimestamp)
            if mtime > _bird_strptime(status['last_reconfiguration']) and (_bird_strptime(status['server_time']) - mtime) >= datetime.timedelta(seconds=params['config_file_min_age']):
                yield Result(state=State.WARN,
                             summary="%s was modified since last reconfiguration" % config_file)
    else:
        yield Result(state=State.UNKNOWN,
                     summary="Unknown status: %s" % status['msg'])

def discover_bird_memory(section) -> DiscoveryResult:
    if 'memory' in section: # bird is running
        yield Service()

def check_bird_memory(params, section) -> CheckResult:
    if 'error' in section:
        yield Result(state=State.CRIT,
                     summary="ERROR: "+section['error'])
        return
    if 'memory' not in section:
        yield Result(state=State.UNKNOWN,
                     summary="No memory data available")
        return
    for name, value_text, value_bytes in section['memory']:
        key = name.replace(" ", "_").split(":")[0]  # memory part wasn't parsed correctly, quick fix
        warn, crit = params.get('memory_levels_'+key, (None, None))
        yield from check_levels(value_bytes,
                                levels_upper=(warn, crit),
                                metric_name=key,
                                render_func=render.bytes,
                                label=name)

def discover_bird_protocols(section) -> DiscoveryResult:
    for protocol in section.get('protocols', {}):
        yield Service(item=protocol, parameters={'protocols': { protocol: section['protocols'][protocol] }})

def check_bird_protocols(item, params, section) -> CheckResult:
    this_time = time.time()
    if 'error' in section:
        yield Result(state=State.CRIT,
                     summary="ERROR: "+section['error'])
        return
    if 'protocols' not in section:
        yield Result(state=State.UNKNOWN,
                     summary="No protocol information available")
        return
    if item not in section.get('protocols', {}):
        yield Result(state=State.UNKNOWN,
                     summary="The protocol no longer exists")
        return
    protocol = section['protocols'][item]
    protocol_inventory = params.get('protocols', {}).get(item)
    if protocol_inventory == None:
        yield Result(state=State.UNKNOWN,
                     summary="inventory data is missing")
        return

    if 'description' in protocol:
        yield Result(state=State.OK,
                     summary=protocol['description'])

    if protocol['state'] in ["up"] or protocol['state'] == protocol_inventory['state']:
        state = State.OK
    elif protocol['state'] in ["start", "wait", "feed"]:
        state = State.WARN
    elif protocol['state'] in ["stop", "flush", "down"]:
        state = State.CRIT
    else:
        state = State.UNKNOWN

    try:
        since_delta = _bird_strptime(section['status']['server_time']) - _bird_strptime(protocol['since'])
        since_str = str(since_delta)
        yield Metric('since', since_delta.total_seconds())
    except ValueError:
        since_str = protocol['since']
    yield Result(state=state,
                 summary="%s since %s" % (protocol['state'], since_str))
    if protocol['info']:
        state = State.OK
        if protocol['proto'] == "OSPF" and protocol['info'] != "Running" and protocol['info'] != protocol_inventory['info']:
            state = State.WARN
        elif protocol['proto'] == "BGP" and protocol['info'] != "Established" and protocol['info'] != protocol_inventory['info']:
            state = State.WARN
        yield Result(state=state,
                     summary=protocol['info'])

    limit_bounds = {}
    for limit_name, limit in protocol.get('limits', {}).items():
        route_stats_levels_key = limit_name.lower().rstrip('e')+"ed"
        crit = limit['value']
        warn = int(params['route_stats_levels_limit_warning_factor']/100.0 * crit)
        limit_bounds[route_stats_levels_key] = { 'upper': (warn, crit) }
        if limit['hit']:
            state = State.CRIT
            if limit['action'] == "warn":
                state = State.WARN
            yield Result(state=state,
                         summary="%s limit (%d) hit" % (limit_name, limit['value']))

    route_stats_levels = params.get('route_stats_levels', {})
    for key, value in protocol.get('route_stats', {}).items():
        bounds = limit_bounds.get(key, {})
        if key in route_stats_levels:
            bounds.update(route_stats_levels[key])
        yield from check_levels(value,
                                levels_upper=bounds.get('upper', (None, None)),
                                levels_lower=bounds.get('lower', (None, None)),
                                metric_name="route_stats_"+key,
                                label=key,
                                notice_only=True)

    this_time = time.time()
    value_store = get_value_store()
    for key, values in protocol.get('route_change_stats', {}).items():
        for field, value in sorted(values):
            if value == None:
                continue

            perfkey = "route_change_stats_%s_%s" % (key, field)
            rate = get_rate(value_store, 'bird_%s' % perfkey, this_time, value)
            yield Metric(perfkey, rate)

    if protocol['proto'] == "OSPF":
        neighbours_count = len(protocol['neighbours'])
        neighbours_inventory_count = len(protocol_inventory['neighbours'])
        yield Metric("neighbours", neighbours_count)

        infotxt = "%i neighbours" % (neighbours_count)
        state = State.OK
        if neighbours_count != neighbours_inventory_count:
            infotxt += " (was %i during inventory)" % (neighbours_inventory_count)
            state = State.WARN
        yield Result(state=state,
                     notice=infotxt)

        for neighbour in protocol['neighbours']:
            neighbour_state = neighbour['State'].split("/")[0]
            if neighbour_state.lower() not in ["full", "2-way"]: # bird <=1.5 state is full, bird >= 1.5 state is Full (uppercase)
                yield Result(state=State.WARN,
                             summary="state of %s is %s" % (neighbour['Router_IP'], neighbour_state))

register.check_plugin(
    name="bird_status",
    service_name="BIRD Status",
    sections=["bird"],
    discovery_function=discover_bird_status,
    check_function=check_bird_status,
    check_default_parameters=_bird_status_default_levels,
    check_ruleset_name="bird_status",
)

register.check_plugin(
    name="bird6_status",
    service_name="BIRD6 Status",
    sections=["bird6"],
    discovery_function=discover_bird_status,
    check_function=check_bird_status,
    check_default_parameters=_bird_status_default_levels,
    check_ruleset_name="bird_status",
)

register.check_plugin(
    name="bird_memory",
    service_name="BIRD Memory",
    sections=["bird"],
    discovery_function=discover_bird_memory,
    check_function=check_bird_memory,
    check_default_parameters={},
    check_ruleset_name="bird_memory",
)

register.check_plugin(
    name="bird6_memory",
    service_name="BIRD6 Memory",
    sections=["bird6"],
    discovery_function=discover_bird_memory,
    check_function=check_bird_memory,
    check_default_parameters={},
    check_ruleset_name="bird6_memory",
)

register.check_plugin(
    name="bird_protocols",
    service_name="BIRD Protocol %s",
    sections=["bird"],
    discovery_function=discover_bird_protocols,
    check_function=check_bird_protocols,
    check_default_parameters=_bird_protocols_default_levels,
    check_ruleset_name="bird_protocols",
)

register.check_plugin(
    name="bird6_protocols",
    service_name="BIRD6 Protocol %s",
    sections=["bird6"],
    discovery_function=discover_bird_protocols,
    check_function=check_bird_protocols,
    check_default_parameters=_bird_protocols_default_levels,
    check_ruleset_name="bird6_protocols",
)
