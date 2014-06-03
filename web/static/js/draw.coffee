
container = document.getElementById 'container'
fc_container = document.getElementById 'fc-container'

_show_loading = () ->
  $('ct-text').text('')
  $('#loading').show()
  $('#ct-view').hide()

_hide_loading = () ->
  $('#loading').hide()
  $('#ct-view').show()

_hide_loading()

fire_post = () ->
  stream_uri = $('#stream_uri').val()
  _show_loading()

  console.log {
    stream_uri:
      stream_uri
    hide_deleted:
      $('#hide_deleted').prop('checked')
  }
  $.post '/cl', {
      stream_uri:
        stream_uri
      hide_deleted:
        $('#hide_deleted').prop('checked')
    },
    (result) ->
      _hide_loading()

      data = result['files']
      idx_table = result['idx_table']

      _cl_fc = _.map data, (l) -> [l[0], if l[1]? then l[1][0] else 0]
      _cl_fc = _.sortBy _cl_fc, (i) -> i[0]
      data = _.sortBy data, (i) -> i[0]

      # data ::= [[ts, [cl_seg_s, cl_seg_e], ...] ...]
      _cl_flattened = _.flatten(_.map(data, (l) -> l[1..]))
      _c_min = _.min(_cl_flattened)
      _c_max = _.max(_cl_flattened)

      stream_title = if stream_uri is '' then 'default stream' else stream_uri

      texts = (for d in data
                 [t, segments...] = d
                 if segments.length == 0
                   continue

                 tf = moment(Math.floor t).format 'YYYY/MM/DD HH:mm:ss'
                 p = idx_table[t.toString() + '.0'][segments[0][0].toString()]
                 "<li>#{tf} #{p}: #{segments}</li>").join('')
      $('#ct-text').text("<ul>#{texts}</ul>")

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
