# encoding: utf-8
from logging import Handler, Formatter, makeLogRecord


class ColoredFormatter(Formatter):
    @staticmethod
    def gen_colorscheme(**kwargs):
        _dict = {'DEBUG': 'gray',
                 'INFO': 'green',
                 'WARNING': 'orange',
                 'ERROR': 'red',
                 'CRITICAL': 'red'}
        for levelname in kwargs:
            _dict[levelname] = kwargs[levelname]

        return _dict

    def __init__(self, fmt=None, datefmt=None, colors=None):
        super(ColoredFormatter, self).__init__(fmt, datefmt)
        if not colors:
            self.colors = {}
        else:
            self.colors = colors

    def format(self, record):
        r = makeLogRecord(record.__dict__)
        for item in self.colors:
            if item == 'asctime':
                info = self.formatTime(r, self.datefmt)
            else:
                info = getattr(r, item)
            setattr(r,
                    item,
                    '<font color=%s>%s</font>' % (self.colors[item](info),
                                                  info))

        r.message = r.getMessage()
        if self.usesTime() and not 'asctime' in self.colors:
            r.asctime = self.formatTime(record, self.datefmt)
        s = self._fmt.format(**r.__dict__)

        return s


class LoggerHandler(Handler):
    def __init__(self, parent):
        super(LoggerHandler, self).__init__()
        self.parent = parent

    def emit(self, record):
        self.parent.signal_new_log.emit(self.format(record))
