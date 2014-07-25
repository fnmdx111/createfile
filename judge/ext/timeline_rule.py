# encoding: utf-8
from judge import Rule
from judge.ext import register
from drive.fs.fat32 import FAT32


class TimelineRule(Rule):

    name = '时间线事件逻辑规则'
    type = FAT32.type

    def __init__(self):
        super().__init__(None, name=self.name)
        self.conclusion = 'My conclusion'
        self.abnormal = True

    def apply_to(self, entries):
        pass
