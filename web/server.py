# encoding: utf-8
from collections import defaultdict
from datetime import datetime
import os
from flask import jsonify, Flask, render_template, request
from drive.disk import get_drive_obj
from drive.fs.fat32 import FAT32
from stream import ImageStream, WindowsPhysicalDriveStream
from web import config
from web.config import partition_log_level
from web.misc import from_js_bool, is_displayable

app = Flask(__name__)

def prepare_partitions(stream_uri):
    if stream_uri:
        stream_type = (WindowsPhysicalDriveStream if stream_uri.startswith('W:')
                       else ImageStream)
        stream = stream_type(stream_uri[2:])
    else:
        stream = config.stream

    partitions = []
    for partition in get_drive_obj(stream):
        if partition:
            partition.logger.setLevel(partition_log_level)
            if partition.type == FAT32.type:
                partitions.append(partition)

    return partitions


def get_cl(stream_uri, show_deleted, show_regular,
                       datetime_start, datetime_end,
                       cluster_start, cluster_end):
    files = []
    fp_idx_table = defaultdict(dict)
    for partition in prepare_partitions(stream_uri):
        entries = partition.get_fdt()

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

    return files, fp_idx_table


@app.route('/<path:fn>')
@app.route('/cl', methods=['POST'])
def get_cluster_lists(fn=''):
    show_deleted = True
    show_regular = True

    if request.method == 'POST':
        fn = request.form['stream_uri']
        show_deleted = from_js_bool(request.form['deleted'])
        show_regular = from_js_bool(request.form['regular'])

        datetime_start = int(request.form['datetime_start']) / 1000
        datetime_end = int(request.form['datetime_end']) / 1000
        cluster_start = int(request.form['cluster_start'])
        cluster_end = int(request.form['cluster_end'])

        if cluster_end == 0:
            cluster_end = 2 ** 32
    else:
        if 'favicon.ico' in fn:
            return b''
        if fn:
            ns = fn.split('/')
            fn = os.path.join(ns[0] + ':/', *ns[1:])

        epoch = datetime.fromtimestamp(0)
        datetime_start = (datetime.min - epoch).total_seconds()
        datetime_end = (datetime.max - epoch).total_seconds()
        cluster_start = 0
        cluster_end = 2 ** 32

    files, fp_idx_table = get_cl(fn, show_deleted, show_regular,
                                 datetime_start, datetime_end,
                                 cluster_start, cluster_end)

    return jsonify(files=files, idx_table=fp_idx_table)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')
