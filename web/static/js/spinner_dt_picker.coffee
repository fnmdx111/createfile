
spinner_ctrl =
  create: (tp_inst, obj, unit, val, min, max, step) ->
    $("<input class='ui-timepicker-input'
              value='#{val}'
              style='width: 50%'>")
      .appendTo(obj)
      .spinner({
        min: min
        max: max
        step: step
        change: (e, ui) ->
          if e.originalEvent isnt undefined
            tp_inst._onTimeChange()
          tp_inst._onSelectHandler()
        spin: (e, ui) ->
          tp_inst.control.value tp_inst, obj, unit, ui.value
          tp_inst._onTimeChange()
          tp_inst._onSelectHandler()
      })
    obj
  options: (tp_inst, obj, unit, opts, val) ->
    if typeof opts == 'string' and val isnt undefined
      obj.find('.ui-timepicker-input').spinner opts, val
    obj.find('.ui-timepicker-input').spinner opts
  value: (tp_inst, obj, unit, val) ->
    if val isnt undefined
      obj.find('.ui-timepicker-input').spinner 'value', val
    obj.find('.ui-timepicker-input').spinner 'value'

$('#dt-start').datetimepicker
  controlType: spinner_ctrl
  dateFormat: 'yy-mm-dd'
  timeFormat: 'HH:mm:ss:l'
$('#dt-end').datetimepicker
  controlType: spinner_ctrl
  dateFormat: 'yy-mm-dd'
  timeFormat: 'HH:mm:ss:l'
