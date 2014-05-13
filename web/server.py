# encoding: utf-8
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


@lru_cache(maxsize=16)
def get_cl(stream_uri):
    files = []
    fp_idx_table = {}
    for partition in prepare_partitions(stream_uri):
        fs, ds = partition.get_fdt()
        for i, (path, obj) in enumerate(fs.items()):
            l = [obj.create_time.timestamp() * 1000]
            l.extend(obj.cluster_list)
            files.append(l)
            fp_idx_table[i] = path
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
    else:
        if 'favicon.ico' in fn:
            return b''
        if fn:
            ns = fn.split('/')
            fn = os.path.join(ns[0] + ':/', *ns[1:])

    files, fp_idx_table = get_cl(fn)

    return jsonify(files=files, idx_table=fp_idx_table)


@app.route('/index')
def index():
    return render_template('index.html')
