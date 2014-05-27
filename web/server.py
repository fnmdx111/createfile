# encoding: utf-8
from collections import defaultdict
from functools import lru_cache
import os
from flask import jsonify, Flask, render_template, request
from drive.disk import get_drive_obj
from drive.fs.fat32 import FAT32
from stream import ImageStream, WindowsPhysicalDriveStream
from web import config

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
            if partition.type == FAT32.type:
                partitions.append(partition)

    return partitions


def get_cl(stream_uri, hide_deleted=False):
    files = []
    fp_idx_table = defaultdict(dict)
    for partition in prepare_partitions(stream_uri):
        entries = partition.get_fdt()
        for ts, obj in entries.iterrows():
            if obj.is_deleted:
                if hide_deleted:
                    continue

            js_timestamp = ts.timestamp() * 1000
            l = [js_timestamp]
            l.extend(obj.cluster_list)
            files.append(l)
            if obj.cluster_list:
                fp_idx_table[js_timestamp][obj.cluster_list[0][0]] =\
                    obj['full_path']
            # files ::= [
            #     [timestamp, [cl_seg_start, cl_seg_end], ...],
            #     ...
            # ]
    return files, fp_idx_table


@app.route('/')
@app.route('/<path:fn>')
@app.route('/cl', methods=['POST'])
def get_cluster_lists(fn=''):
    if request.method == 'POST':
        fn = request.form['stream_uri']
        hide_deleted = request.form['hide_deleted']
    else:
        if 'favicon.ico' in fn:
            return b''
        if fn:
            ns = fn.split('/')
            fn = os.path.join(ns[0] + ':/', *ns[1:])
        hide_deleted = False

    files, fp_idx_table = get_cl(fn, hide_deleted)

    return jsonify(files=files, idx_table=fp_idx_table)


@app.route('/index')
def index():
    return render_template('index.html')
