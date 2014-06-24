# encoding: utf-8
"""
    web.server
    ~~~~~~~~~~

    This module implement the routes and actually server reactions of the web
    interface.
"""
from datetime import datetime
import os
from flask import jsonify, Flask, render_template, request
from web.misc import from_js_bool, get_cl

app = Flask(__name__)

@app.route('/<path:fn>')
@app.route('/cl', methods=['POST'])
def get_cluster_lists(fn=''):
    """Get cluster lists. Handler function for request `cl`.

    :param fn: optional, image path used by :class:`ImageStream`.
    """

    show_deleted = True
    show_regular = True

    if request.method == 'POST':
        fn = request.form['stream_uri']
        use_cache = from_js_bool(request.form['use_cache'])

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

        use_cache = False

        epoch = datetime.fromtimestamp(0)
        datetime_start = (datetime.min - epoch).total_seconds()
        datetime_end = (datetime.max - epoch).total_seconds()
        cluster_start = 0
        cluster_end = 2 ** 32

    files, fp_idx_table = get_cl(fn, show_deleted, show_regular,
                                 datetime_start, datetime_end,
                                 cluster_start, cluster_end,
                                 use_cache)

    return jsonify(files=files, idx_table=fp_idx_table)


@app.route('/')
@app.route('/index')
def index():
    """Handler function for request `/` and `index`."""

    return render_template('index.html')
