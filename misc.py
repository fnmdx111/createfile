# encoding: utf-8
"""
    misc
    ~~~~

    Miscellaneous functions used by `createfile`.
"""
import time
import matplotlib.dates as mdt

MAGIC_END_SECTION = b'\x55\xaa'

STATE_DOS_ENTRY = 0b01
STATE_LFN_ENTRY = 0b10
STATE_START = 0b11


def clear_cur_obj(obj):
    """Clear contents of the state machine.

    :param obj: the state machine contents holder.
    """

    obj['name'] = ''
    obj['checksum'] = 0


def time_it(f):
    """A decorator which times the decorated function.

    :param f: function to time.
    """

    def wrapper(*args, **kwargs):
        t1 = time.time()
        ret = f(*args, **kwargs)
        t2 = time.time()

        print('"%s" time elapsed: %0.2f' % (f.__name__, (t2 - t1)))

        return ret

    return wrapper


class SimpleCounter:
    """
    A simple counter.
    """
    __slots__ = ['counter']

    def __init__(self, initial=0):
        """
        :param initial: initial value of the counter.
        """

        self.counter = initial

    def inc(self, n=1):
        """Increase the counter by n.

        :param n: optional, value to add.
        """

        self.counter += n

    def dec(self, n=1):
        """Decrease the counter by n.

        :param n: optional, value to substract.
        """

        self.counter -= n

    def __str__(self):
        return str(self.counter)

    def __repr__(self):
        return repr(self.counter)

    def __lt__(self, other):
        if isinstance(other, self):
            other = other.counter
        return self.counter < other

    def __eq__(self, other):
        return self.counter == other.counter

    def __hash__(self):
        return hash(self.counter)

    def __int__(self):
        return self.counter


class StateManager:
    """
    Class that manages the states of the LFN state machine.
    """
    def __init__(self, init_state):
        """
        :param init_state: initial state.
        """

        self._state = init_state

    def transit_to(self, state):
        """Transit to specified state.

        :param state: the specified state to transit to.
        """

        self._state = state

    def is_(self, state):
        """Tests if current state is the same as the given state.

        :param state: state to test against.
        """

        return self._state == state


def setup_axis_datetime(axis):
    auto_locator = mdt.AutoDateLocator()
    auto_formatter = mdt.AutoDateFormatter(auto_locator)

    auto_formatter.scaled = {
        365.0: '%Y',
        30.: '%Y-%m',
        1.: '%Y-%m-%d',
        1. / 24.: '%H:%M:%S',
        1. / (24. * 60.): '%H:%M:%S.%f'
    }

    axis.set_major_locator(auto_locator)
    axis.set_major_formatter(auto_formatter)


class InvalidRecordException(Exception):
    def __init__(self, msg=''):
        super(InvalidRecordException, self).__init__(msg)
        self._msg = msg

    def __str__(self):
        return "InvalidRecordException(%s)" % (self._msg)


class MFTExhausted(BaseException):
    pass
