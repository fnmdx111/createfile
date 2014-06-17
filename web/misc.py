# encoding: utf-8

from_js_bool = lambda b: b == 'true'

def _filter(entry,
            dts, dte,
            cs, ce):
    if entry.cluster_list:
        if cs < entry.cluster_list[0][0] < entry.cluster_list[-1][-1] < ce:
            return dts < entry.create_time.timestamp() < dte
        else:
            return False
    else:
        return True


def is_displayable(entry,
                   sd, sr,
                   dts, dte,
                   cs, ce):
    if entry.is_deleted:
        if sd:
            return _filter(entry, dts, dte, cs, ce)
    else:
        if sr:
            return _filter(entry, dts, dte, cs, ce)

    return False
