
container = document.getElementById 'container'

_show_loading = () ->
  $('#loading').show()
  $('#ct-view').hide()

_hide_loading = () ->
  $('#loading').hide()
  $('#ct-view').show()

_hide_loading()

fire_post = () ->
  stream_uri = $('#stream_uri').val()
  _show_loading()

  $.post '/cl',
    stream_uri: stream_uri
    (result) ->
      _hide_loading()

      data = result['files']
      idx_table = result['idx_table']

      # data ::= [[path, ts, [cl_seg_s, cl_seg_e], ...] ...]
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
          labelsAngle: 45
          autoscale: on
        yaxis:
          autoscale: on
          min: _c_min
          max: _c_max
          margin: true
        selection:
          mode: 'xy'
        title: "CT View - #{stream_title}"
        # mouse:
          # track: on
          # relative: yes

      draw_graph = (opts) ->
        Flotr.draw container, [data], Flotr._.extend(Flotr._.clone(options),
                                                   opts || {})

      graph = draw_graph()

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

      Flotr.EventAdapter.observe container, 'flotr:click', () ->
        graph = draw_graph()

$('#fire_post').click fire_post

shortcut.add 'enter', () ->
  fire_post()
