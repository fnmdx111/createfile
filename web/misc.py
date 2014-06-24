# encoding: utf-8
"""
    web.misc
    ~~~~~~~~

    This module implements several miscellaneous classes and functions important
    for the web interface.
"""
from collections import defaultdict
from drive.fs.fat32 import FAT32
from drive.disk import get_drive_obj
from stream import ImageStream, WindowsPhysicalDriveStream
from . import config as cfg

from_js_bool = lambda b: b == 'true'

def _filter(entry,
            dts, dte,
            cs, ce):
    """Predicate for determining whether an entry is visible. It only considers
    time and cluster.

    :param entry: the entry to be determined.
    :param dts, dte: starting and ending date times.
    :param cs, ce: starting and ending clusters.
    """

    if entry.cluster_list:
        if cs <= entry.cluster_list[0][0] <= entry.cluster_list[-1][-1] <= ce:
            return dts <= entry.create_time.timestamp() <= dte
        else:
            return False
    else:
        return True


def is_displayable(entry,
                   sd, sr,
                   dts, dte,
                   cs, ce):
    """Predicate for determining whether an entry is visible. It filters deleted
    files on demand.

    :param entry: entry to be determined.
    :param sd, sr: bool values representing showing deleted and showing regular
                   files.
    :param dts, dte: starting and ending date times.
    :param cs, ce: starting and ending clusters.
    """

    if entry.is_deleted:
        if sd:
            return _filter(entry, dts, dte, cs, ce)
    else:
        if sr:
            return _filter(entry, dts, dte, cs, ce)

    return False


def prepare_partitions(stream_uri):
    """Prepare partitions according to the URI representing which stream to
    use."""

    if stream_uri:
        stream_type = (WindowsPhysicalDriveStream if stream_uri.startswith('W:')
                       else ImageStream)
        stream = stream_type(stream_uri[2:])
    else:
        stream = cfg.stream

    partitions = []
    for partition in get_drive_obj(stream):
        if partition:
            partition.logger.setLevel(cfg.partition_log_level)
            partitions.append(partition)

    return partitions


class FakeFAT32:
    """
    A mocking of the FAT32 class.
    """
    type = FAT32.type

    def __init__(self, entries):
        self.entries = entries

    def get_fdt(self):
        return self.entries


entries_cache = {}
def get_cl(stream_uri, show_deleted, show_regular,
                       datetime_start, datetime_end,
                       cluster_start, cluster_end,
                       use_cache):
    """Get result for `cl` requests.

    :param stream_uri: URI of stream to use.
    :param show_deleted: whether to show deleted files.
    :param show_regular: whether to show regular files.
    :param datetime_start: starting date time.
    :param datetime_end: ending date time.
    :param cluster_start: starting cluster.
    :param cluster_end: ending cluster.
    :param use_cache: whether to use results from cache.
    """

    files = []
    fp_idx_table = defaultdict(dict)

    if use_cache and stream_uri in entries_cache:
        partitions = entries_cache[stream_uri]
        record = False
    else:
        partitions = prepare_partitions(stream_uri)
        record = True

    _p_cache = []
    for partition in partitions:
        if partition.type != FAT32.type:
            continue

        entries = partition.get_fdt()
        if record:
            _p_cache.append(FakeFAT32(entries))

        for ts, obj in entries.iterrows():
            if not is_displayable(obj, show_deleted, show_regular,
                                       datetime_start, datetime_end,
                                       cluster_start, cluster_end):
                continue

            js_timestamp = ts.timestamp() * 1000
            l = [obj.full_path, js_timestamp]
            l.extend(obj.cluster_list)
            files.append(l)
            if obj.cluster_list:
                # fp_idx_table is reserved due to compatibility reasons
                fp_idx_table[js_timestamp][obj.cluster_list[0][0]] =\
                    obj.full_path
            # files ::= [
            #     [fp, timestamp, [cl_seg_start, cl_seg_end], ...],
            #     ...
            # ]

    if record:
        entries_cache[stream_uri] = _p_cache

    return files, fp_idx_table
