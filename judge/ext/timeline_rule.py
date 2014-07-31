# encoding: utf-8
import datetime as dt

from .. import Rule
from . import register
from drive.fs.fat32 import FAT32


@register
class TimelineRule(Rule):

    name = '时间线事件逻辑规则'
    type = FAT32.type
    conclusion = '时间线事件逻辑异常'
    abnormal = True

    def __init__(self):
        super().__init__(None)

    def do_apply(self, entries):
        entries = entries.sort(columns=['first_cluster'])
        self._pending_return_values(entries)

        for i, (_, o) in enumerate(entries.iterrows()):
            if i == 0 or i == entries.shape[0] - 1:
                continue

            prev, this, next_ = entries.iloc[i - 1], o, entries.iloc[i + 1]
            if (abs(next_.create_time - prev.create_time)
                    < dt.timedelta(seconds=3)):
                if prev.conclusions == next_.conclusions:
                    if (abs(this.create_time - prev.create_time)
                            > dt.timedelta(seconds=2)):
                        self.mark_as_positive(i)
