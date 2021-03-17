#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from functools import reduce

metric_info['Routing_tables'] = {
    'title': _('Routing Tables'),
    'unit': 'bytes',
    "color" : "#00e060",
}

metric_info['Route_attributes'] = {
    'title': _('Route Attributes'),
    'unit': 'bytes',
    "color" : "#0080e0",
}

metric_info['ROA_tables'] = {
    'title': _('ROA Tables'),
    'unit': 'bytes',
    "color" : "#cc00ff",
}

metric_info['Protocols'] = {
    'title': _('Protocols'),
    'unit': 'bytes',
    "color" : "#f900ff",
}

metric_info['Total'] = {
    'title': _('Total'),
    'unit': 'bytes',
    "color" : "#ff4c00",
}

metric_info['time_since_last_reconfiguration'] = {
    'title': _('Time since last reconfiguration'),
    'unit': 's',
    'color': '#cc00ff',
}

metric_info['route_stats_imported'] = {
    'title': _('Prefixes Imported'),
    'unit': 'count',
    'color': '#cc00ff',
}

metric_info['route_stats_exported'] = {
    'title': _('Prefixes Exported'),
    'unit': 'count',
    'color': '#f900ff',
}

metric_info['route_stats_preferred'] = {
    'title': _('Prefixes Preferred'),
    'unit': 'count',
    'color': '#ff4c00',
}

metric_info['since'] = {
    'title': _('Since'),
    'unit': 's',
    'color': '#cc00ff',
}

def bird_color(i, j, k):
    a = reduce(lambda x, y: x + ord(y), i, 0)
    b = reduce(lambda x, y: x + ord(y), j, 0)
    c = reduce(lambda x, y: x + ord(y), k, 0)
    return hex( (a * b * c) % 16777216)[2:].zfill(6)

for i in ['Import', 'Export']:
    for j in ['updates', 'withdraws']:
        for k in ['accepted', 'filtered', 'ignored', 'received', 'rejected']:
            metric_info['route_change_stats_%s_%s_%s' % (i, j, k)] = {
                'title': _('%s %s %s' % (i, j, k)),
                'unit': '1/s',
                'color': '#%s' % bird_color(i, j, k),
            }
