# encoding: utf-8
from stats.misc import windowed
import numpy as np
import matplotlib.pyplot as plt
try:
    # try import this lib to prettify the original plots
    # if it is not installed, fallback to plt
    import prettyplotlib as ppl
except ImportError:
    ppl = plt


def get_windowed_metrics(fs, entries, fn=None, echo=True, plot=True):
    fn = fn or [f.__name__ for f in fs]

    w_cnt, values = 0, [[] for _ in fs]
    for w in windowed(list(entries.iterrows()), size=5, step=1):
        w = tuple(w)

        for i, f in enumerate(fs):
            v = f(np.array(list(map(lambda x: x[1].first_cluster,
                                    w))),
                  np.array(list(map(lambda x: x[1].create_time
                                                  .timestamp() * 1000,
                                    w))))
            values[i].append(v)

        if echo:
            print('window %s:' % w_cnt)
            print('{0[0]}\n\t{0[1]}\n'
                  '{1[0]}\n\t{1[1]}\n'
                  '{2[0]}\n\t{2[1]}\n'
                  '{3[0]}\n\t{3[1]}\n'
                  '{4[0]}\n\t{4[1]}'.format(*map(lambda x: (x[1].full_path,
                                                            x[1].first_cluster),
                                                 w)))
            for n, v in zip(fn, values):
                print('%s: %s' % (n, v[w_cnt]))
            print('----------------')

        w_cnt += 1

    if plot:
        plots = []
        for n, v in zip(fn, values):
            plots.append(ppl.plot(v, label=n)[0])
        ppl.legend(plots, fn)
        plt.show()

    return values
