# encoding: utf-8

from .settings import SettingsDialog
from .figure import FigureDialog
from .files import FilesDialog
from .log import LogDialog
from .partitions import PartitionsDialog
from .auth_time_deduct import AuthenticCreateTimeDeductionDialog
from .summary import SummaryDialog

__all__ = ['SettingsDialog', 'FigureDialog', 'FilesDialog', 'LogDialog',
           'PartitionsDialog', 'AuthenticCreateTimeDeductionDialog',
           'SummaryDialog']
