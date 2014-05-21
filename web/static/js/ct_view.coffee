Flotr.addType 'ct_view',
  options:
    show: no
    lineWidth: 2
    barWidth: 1
    fill: yes
    fillColor: null
    fillOpacity: 0.4
    horizontal: no
    centered: yes
    realData: _.identity
    topPadding: 0.1

  draw: (options) ->
    context = options.context
    @current += 1

    context.save()
    context.lineJoin = 'miter'
    context.lineWidth = options.lineWidth
    context.strokeStyle = options.color
    context.fillStyle = options.fillStyle if options.fill

    @plot options

    context.restore()

  plot: (options) ->
    data = options.data
    context = options.context
    shadowSize = options.shadowSize

    return if data.length < 1

    @translate context, options.horizontal

    for d_ in data
      d = options.realData(d_)
      # d ::= [ts, [[cl0_s, cl0_e], [cl1_s, cl1_e], ..., [cln_s, cln_e]]]
      [x, cl_segments...] = d
      for cl_segment in cl_segments
        geometry = @getBarGeometry x, cl_segment, options
        continue if geometry is null

        [left, top, width, height] = [geometry.left, geometry.top,
                                      geometry.width, geometry.height]

        if options.fill
          context.fillRect left, top, width, height

        if shadowSize
          context.save()
          context.fillStyle = 'rgba(0, 0, 0, 0.05)'
          context.fillRect left + shadowSize, top + shadowSize, width, height
          context.restore()

        if options.lineWidth
          context.strokeRect left, top, width, height

  translate: (context, horizontal) ->
    if horizontal
      context.rotate -Math.PI / 2
      context.scale -1, 1

  getBarGeometry: (x, y, options) ->
    # x ::= timestamp
    # y ::= [ys, ye]

    barWidth = options.barWidth
    bisection = if options.centered then barWidth / 2 else 0

    horizontal = options.horizontal
    xScale = if horizontal then options.yScale else options.xScale
    yScale = if horizontal then options.xScale else options.yScale
    xValue = if horizontal then y else x
    yValue = if horizontal then x else y
    [ysValue, yeValue] = yValue

    scaled_x = (xScale xValue) - bisection

    left   = scaled_x
    right  = scaled_x + barWidth
    top    = yScale yeValue
    bottom = yScale ysValue

    bottom = 0 if bottom < 0
    height = bottom - top

    lineWidth = options.lineWidth

    return if x is null or y is null then null else {
      x     : xValue
      y     : yValue
      xScale: xScale
      yScale: yScale
      top   : top
      left  : Math.min(left, right) - lineWidth / 2
      width : Math.abs(right - left) - lineWidth
      height: if height > 0 then height else 0.7
    }

  hit: (options) ->
    data = options.data
    [mouse, n] = options.args
    x = options.xInverse mouse.relX
    y = options.yInverse mouse.relY
    hitGeometry = @getBarGeometry x, y, options
    width = hitGeometry.width / 2
    left = hitGeometry.left
    height = hitGeometry.y

    i = data.length
    while i--
      d = options.realData(data[i])
      geometry = @getBarGeometry d[0], d[1], options
      if (geometry.y[0] < height < geometry.y[1] or
          geometry.y[0] > height > geometry.y[1]) and
         Math.abs(left - geometry.left) < width
        [n.x, n.y] = d
        n.index = i
        n.seriesIndex = options.index

  drawHit: (options) ->
    context = options.context
    args = options.args
    geometry = @getBarGeometry args.x, args.y, options
    [left, top, width, height] = [geometry.left
                                  geometry.top
                                  geometry.width
                                  geometry.height]

    context.save()
    context.strokeStyle = options.color
    context.lineWidth = options.lineWidth
    @translate(context, options.horizontal)

    context.beginPath()
    context.moveTo left, top + height
    context.lineTo left, top
    context.lineTo left + width, top
    context.lineTo left + width, top + height
    context.lineTo left, top + height
    if options.fill
      context.fillStyle = options.fillStyle
      context.fill()
    context.stroke()
    context.closePath()

    context.restore()

  clearHit: (options) ->
    context = options.context
    args = options.args
    geometry = @getBarGeometry args.x, args.y, options
    [left, top, width, height] = [geometry.left
                                  geometry.top
                                  geometry.width
                                  geometry.height]
    lineWidth = 2 * options.lineWidth

    context.save()
    @translate context, options.horizontal
    context.clearRect left - lineWidth,
                      Math.min(top, top + height) - lineWidth,
                      width + 2 * lineWidth,
                      Math.abs(height) + 2 * lineWidth
    context.restore()

  # extendXRange: (axis, data, options, bars) ->
    # @_extendRange(axis, data, options, bars)
    # @current = 0


