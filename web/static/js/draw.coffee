
container = document.getElementById 'container'
fc_container = document.getElementById 'fc-container'

_data = []

_show_loading = () ->
  $('ct-text').text('')
  $('#loading').show()
  $('#ct-view').hide()

_hide_loading = () ->
  $('#loading').hide()
  $('#ct-view').show()

_hide_loading()

fill_ct_text = (method) ->
  if method is 'time'
    _d = _.sortBy _data, (i) -> i[1]
  else if method is 'fc'
    _d = _.sortBy _data, (i) ->
      if i.length > 2
        parseInt i[2][0]
      else
        0

  texts = (for d in _d
    [fp, t, segments...] = d
    if segments.length == 0
      segments = 'empty cluster list'

    tf = moment(Math.floor t).format 'YYYY/MM/DD HH:mm:ss'
    "<li>#{tf} #{fp}: #{segments}</li>").join('')
  $('#ct-text').html("<p>#{_d.length} file(s) in total.</p>" +
                     "<ul>#{texts}</ul>")

$('#ctc-time').click () -> fill_ct_text 'time'
$('#ctc-fc').click () -> fill_ct_text 'fc'

fire_post = () ->
  stream_uri = $('#stream_uri').val()
  _show_loading()

  $.post '/cl', {
      stream_uri:
        stream_uri
      deleted:
        $('#deleted').prop('checked')
      regular:
        $('#regular').prop('checked')
    },
    (result) ->
      _hide_loading()

      data = result['files']
      idx_table = result['idx_table']

      _data = $.extend {}, data

      data = _.map data, (l) -> l[1..]

      _cl_fc = _.map data, (l) -> [l[0], if l[1]? then l[1][0] else 0]
      _cl_fc = _.sortBy _cl_fc, (i) -> i[0]
      data = _.sortBy data, (i) -> i[0]

      # data ::= [[ts, [cl_seg_s, cl_seg_e], ...] ...]
      _cl_flattened = _.flatten(_.map(data, (l) -> l[1..]))
      _c_min = _.min(_cl_flattened)
      _c_max = _.max(_cl_flattened)

      stream_title = if stream_uri is '' then 'default stream' else stream_uri


      options =
        ct_view:
          show: yes
          horizontal: no
          shadowSize: 0.5
          barWidth: 10
          HtmlText: no
          topPadding: 10
        xaxis:
          mode: 'time'
          noTicks: 12 # automatically set this number against the data
          labelsAngle: 45
          autoscale: on
        yaxis:
          autoscale: on
          min: _c_min
          max: _c_max
          margin: true
        selection:
          mode: 'xy'
        title: "CT Plot - #{stream_title}"
        mouse:
          track: on
          relative: yes
          trackFormatter: (obj) ->
            date = moment(Math.floor obj.x).format 'YYYY/MM/DD HH:mm:ss'
            path = idx_table[obj.x.toString()][obj.y[0].toString()]
            "#{path} ::= cl: #{obj.y}, ts: #{date}"
      fc_options =
        line:
          show: yes
        xaxis:
          mode: 'time'
          noTicks: 12
          labelsAngle: 45
          autoscale: on
        yaxis:
          autoscale: on
          min: _c_min
          max: _c_max
          margin: true
        selection:
          mode: 'xy'
        title: "FC Plot - #{stream_title}"

      draw_graph = (opts) ->
        Flotr.draw container, [data],
                   Flotr._.extend(Flotr._.clone(options), opts || {})
      draw_fc_graph = (opts) ->
        Flotr.draw fc_container, [_cl_fc],
                   Flotr._.extend(Flotr._.clone(fc_options), opts || {})

      graph = draw_graph()
      fc_graph = draw_fc_graph()

      Flotr.EventAdapter.observe container, 'flotr:select', (area) ->
        graph = draw_graph
          xaxis:
            min: area.x1
            max: area.x2
            mode: 'time'
            labelsAngle: 45
          yaxis:
            min: area.y1
            max: area.y2

        fc_graph = draw_fc_graph
          xaxis:
            min: area.x1
            max: area.x2
            mode: 'time'
            labelsAngle: 45
          yaxis:
            min: area.y1
            max: area.y2

      Flotr.EventAdapter.observe container, 'flotr:click', () ->
        graph = draw_graph()
        fc_graph = draw_fc_graph()

$('#fire_post').click fire_post

shortcut.add 'enter', () ->
  fire_post()
