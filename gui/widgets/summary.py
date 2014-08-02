# encoding: utf-8
from collections import defaultdict

from PySide.QtGui import *
import jinja2

from stats import statistical_summary_of


class SummaryWidget(QWidget):

    template = jinja2.Template(
        '''<p>
分区共有
{{ abnormal_counter[True] + abnormal_counter[False] }}
个可用文件项目。{%- if file_type_counter -%}其中<ul>
{% for suffix in file_type_counter %}
    <li><b><font color='blue'>{{ suffix }}文件</font></b>共有
{{ file_type_counter[suffix] }} 个</li>
{% endfor %}</ul>
{%- endif %}
正常文件共 {{ abnormal_counter[False] }}
个，异常文件共 {{ abnormal_counter[True] }} 个。
</p>

<p>
首次使用时间: {{ min_st }}，<br />
最后使用时间: {{ max_et }}。<br />
<br />
在这期间共有 {{ (max_et - min_st).days }} 天，实际有操作行为的共有
{{ days_counter|count }}
天。{% if conclusion_counter -%}在这些天中有:
<ul>
{% for c in conclusion_counter %}
    {% if rules_category[c] == False %}
        {% set color = 'green' %}
    {% else %}
        {% set color = 'red' %}
    {% endif %}
    <li><b><font color='{{ color }}'>{{ c }}</font></b>共
{{ conclusion_counter[c] }} 次</li>
{% endfor %}
</ul>
{%- endif %}
</p>'''
    )

    def __init__(self, parent, partition_type):
        super().__init__(parent=parent)

        self._parent = parent

        self.text_browser = QTextBrowser()
        _l = QVBoxLayout()
        _l.addWidget(self.text_browser)
        self.setLayout(_l)

        self.text_browser.setReadOnly(True)

        self.start_time = None
        self.end_time = None

        self.conclusions = defaultdict(int)

        self.partition_type = partition_type

        self.summary_text = ''

    def set_start_time(self, start_time):
        self.start_time = start_time

    def set_end_time(self, end_time):
        self.end_time = end_time

    def add_conclusion(self, conclusion, n):
        self.conclusions[conclusion] = n

    def clear(self):
        self.start_time = None
        self.end_time = None
        self.conclusions.clear()
        self.summary_text = ''

    def set_summary(self, summary=''):
        s = summary or self.summary_text

        self.text_browser.clear()
        self.text_browser.setHtml(s)

    def summarize(self, entries):
        self.clear()

        (min_st, max_et), dc, ftc, cc, ac, rc = statistical_summary_of(
            self.partition_type,
            self._parent.rules_widget.rules(),
            entries
        )

        self.set_start_time(min_st)
        self.set_end_time(max_et)

        self.summary_text = self.template.render(min_st=min_st,
                                                 max_et=max_et,
                                                 days_counter=dc,
                                                 file_type_counter=ftc,
                                                 conclusion_counter=cc,
                                                 abnormal_counter=ac,
                                                 rules_category=rc)

        return self.summary_text
