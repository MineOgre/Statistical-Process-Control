
"""
SPC Statistical Process Control provides means to monitor process behaviour
using statistical tools defined by Shewhart and others. The process run is shown
as Quality Control Charts (QCC).
Author: Michal Nowikowski <godfryd@gmail.com>
License: MIT
"""

"""
Edited by Mine Öğretir
Added: Missing Rules
Some changes
Changepoint is added, when changepoints are set, the calculations are made in the intervals individually

"""

import numpy as np


CHART_X_BAR_R_X = "x_bar R - X"
CHART_X_BAR_R_R = "x_bar R - R"
CHART_X_BAR_S_X = "x_bar S - X"
CHART_X_BAR_S_S = "x_bar S - S"
CHART_X_MR_X = "X mR - X"
CHART_X_MR_MR = "X mR - mR"
CHART_P = "p"
CHART_NP = "np"
CHART_C = "c"
CHART_U = "u"
CHART_EWMA = "EWMA"
CHART_CUSUM = "CUSUM"
CHART_THREE_WAY = "three way"
CHART_TIME_SERIES = "time series"

RULES_1_BEYOND_3SIGMA = "1 beyond 3*sigma"
RULES_2_OF_3_BEYOND_2SIGMA = "2 of 3 beyond 2*sigma"
RULES_4_OF_5_BEYOND_1SIGMA = "4 of 5 beyond 1*sigma"
RULES_7_ON_ONE_SIDE = "7 on one side"
RULES_8_ON_ONE_SIDE = "8 on one side"
RULES_9_ON_ONE_SIDE = "9 on one side"
RULES_6_TRENDING = "6 trending"
RULES_14_UP_DOWN = "14 up down"
RULES_15_BELOW_1SIGMA = "15 below 1*sigma"
RULES_8_BEYOND_1SIGMA_BOTH_SIDES = "8 beyond 1*sigma on both sides"

RULES_BASIC = [RULES_1_BEYOND_3SIGMA,
               RULES_7_ON_ONE_SIDE]
RULES_PMI = [RULES_1_BEYOND_3SIGMA,
             RULES_8_ON_ONE_SIDE]
RULES_WECO = [RULES_1_BEYOND_3SIGMA,
              RULES_2_OF_3_BEYOND_2SIGMA,
              RULES_4_OF_5_BEYOND_1SIGMA,
              RULES_8_ON_ONE_SIDE,
              RULES_6_TRENDING, RULES_14_UP_DOWN]
RULES_NELSON = [RULES_1_BEYOND_3SIGMA,
                RULES_9_ON_ONE_SIDE,
                RULES_6_TRENDING,
                RULES_14_UP_DOWN,
                RULES_2_OF_3_BEYOND_2SIGMA,
                RULES_4_OF_5_BEYOND_1SIGMA,
                RULES_15_BELOW_1SIGMA,
                RULES_8_BEYOND_1SIGMA_BOTH_SIDES]

RULES_ALL = [RULES_1_BEYOND_3SIGMA,
             RULES_2_OF_3_BEYOND_2SIGMA,
             RULES_4_OF_5_BEYOND_1SIGMA,
             RULES_7_ON_ONE_SIDE,
             RULES_8_ON_ONE_SIDE,
             RULES_9_ON_ONE_SIDE,
             RULES_6_TRENDING,
             RULES_14_UP_DOWN,
             RULES_15_BELOW_1SIGMA,
             RULES_8_BEYOND_1SIGMA_BOTH_SIDES]


def test_beyond_limits(data, center, lcl, ucl):
    return data[0] > ucl or data[0] < lcl


def test_violating_runs(data, center, lcl, ucl):
    for i in range(1, len(data)):
        if (data[i-1] - center)*(data[i] - center) < 0:
            return False
    return True

def test_beyond_2_sigma(data, center, lcl, ucl):
    cnt = 0
    for i in range(len(data)):
        if data[i] > center+(ucl-center)*2/3:
            cnt +=1
    if cnt>1:
        return True
    cnt = 0
    for i in range(len(data)):
        if data[i] < center-(center-lcl)*2/3:
            cnt +=1
    if cnt>1:
        return True
    return False


def test_beyond_1_sigma(data, center, lcl, ucl):
    cnt = 0
    for i in range(len(data)):
        if data[i] > center+(ucl-center)/3:
            cnt +=1
    if cnt>3:
        return True
    cnt = 0
    for i in range(len(data)):
        if data[i] < center-(center-lcl)/3:
            cnt +=1
    if cnt>3:
        return True
    return False

def test_below_1_sigma(data, center, lcl, ucl):
    for i in range(len(data)):
        if data[i] > center+(ucl-center)/3 and data[i] > center:
            return False
    for i in range(len(data)):
        if data[i] < center-(center-lcl)/3 and data[i] < center:
            return False
    return True

def test_trending(data, center, lcl, ucl):
    if data[1] > data[0]:
        for i in range(1, len(data)-1):
            if data[i+1] <= data[i]:
                return False
    if data[1] < data[0]:
        for i in range(1, len(data)-1):
            if data[i+1] >= data[i]:
                return False
    if data[1] != data[0]:
        return True
    return False

def test_up_down(data, center, lcl, ucl):
    for i in range(len(data)-2):
        if data[i+1] < data[i]:
            if data[i+2] < data[i+1]:
                return False
        if data[i+1] > data[i]:
            if data[i+2] > data[i+1]:
                return False
    return True

def test_beyond_1_sigma_both_sides(data, center, lcl, ucl):
    for i in range(len(data)):
        if data[i] < center+(ucl-center)/3 and data[i] > center-(center-lcl)/3:
            return False
    return True

# n         2      3      4      5      6      7      8      9      10
A2 = [0, 0, 1.880, 1.023, 0.729, 0.577, 0.483, 0.419, 0.373, 0.337, 0.308]
D3 = [0, 0, 0, 0, 0, 0, 0, 0.076, 0.136, 0.184, 0.223]
D4 = [0, 0, 3.267, 2.575, 2.282, 2.115, 2.004, 1.924, 1.864, 1.816, 1.777]
# n   0 1      2      3      4      5      6      7      8      9     10
# 11     12     13     14     15       20     25
c4 = [0, 0, 0.7979, 0.8862, 0.9213, 0.9400, 0.9515, 0.9594, 0.9650,
      0.9693, 0.9727, 0.9754, 0.9776, 0.9794, 0.9810, 0.9823]  # 0.9869, 0.9896]
B3 = [0, 0, 0, 0, 0, 0, 0.030, 0.118, 0.185, 0.239, 0.284, 0.321,
      0.354, 0.382, 0.406, 0.428]  # 0.510, 0.565]
B4 = [0, 0, 3.267, 2.568, 2.266, 2.089, 1.970, 1.882, 1.815, 1.761,
      1.716, 1.679, 1.646, 1.618, 1.594, 1.572]  # 1.490, 1.435]
B5 = [0, 0, 0, 0, 0, 0, 0.029, 0.113, 0.179, 0.232, 0.276, 0.313,
      0.346, 0.374, 0.399, 0.421]  # 0.504, 0.559]
B6 = [0, 0, 2.606, 2.276, 2.088, 1.964, 1.874, 1.806, 1.751, 1.707,
      1.669, 1.637, 1.610, 1.585, 1.563, 1.544]  # 1.470, 1.420]
A3 = [0, 0, 2.659, 1.954, 1.628, 1.427, 1.287, 1.182, 1.099, 1.032,
      0.975, 0.927, 0.886, 0.850, 0.817, 0.789]  # 0.680, 0.606]


def get_stats_x_mr_x(data, size):
    assert size == 1
    center = np.mean(data)
    sd = 0
    for i in range(len(data)-1):
        sd += abs(data[i] - data[i+1])
    sd /= len(data) - 1
    d2 = 1.128
    lcl = center - 3*sd/d2
    ucl = center + 3*sd/d2
    return center, lcl, ucl


def get_stats_x_mr_mr(data, size):
    assert size == 1
    sd = 0
    for i in range(len(data)-1):
        sd += abs(data[i] - data[i+1])
    sd /= len(data) - 1
    d2 = 1.128
    center = sd
    lcl = 0
    ucl = center + 3*sd/d2
    return center, lcl, ucl


def get_stats_x_bar_r_x(data, size):
    n = size
    assert n >= 2
    assert n <= 10

    r_sum = 0
    for xset in data:
        assert len(xset) == n
        r_sum += max(xset) - min(xset)
    r_bar = r_sum / len(data)

    x_bar = np.mean(data)

    center = x_bar
    lcl = center - A2[n]*r_bar
    ucl = center + A2[n]*r_bar
    return center, lcl, ucl


def get_stats_x_bar_r_r(data, size):
    n = size
    assert n >= 2
    assert n <= 10

    r_sum = 0
    for xset in data:
        assert len(xset) == n
        r_sum += max(xset) - min(xset)
    r_bar = r_sum / len(data)

    center = r_bar
    lcl = D3[n]*r_bar
    ucl = D4[n]*r_bar
    return center, lcl, ucl


def get_stats_x_bar_s_x(data, size):
    n = size
    assert n >= 2
    assert n <= 10

    s_bar = np.mean(np.std(data, 1, ddof=1))
    x_bar = np.mean(data)

    center = x_bar
    lcl = center - A3[n]*s_bar
    ucl = center + A3[n]*s_bar
    return center, lcl, ucl


def get_stats_x_bar_s_s(data, size):
    n = size
    assert n >= 2
    assert n <= 10

    s_bar = np.mean(np.std(data, 1, ddof=1))

    center = s_bar
    lcl = B3[n]*s_bar
    ucl = B4[n]*s_bar
    return center, lcl, ucl


def get_stats_p(data, size):
    n = size
    assert n > 1

    pbar = float(sum(data)) / (n * len(data))
    sd = np.sqrt(pbar*(1-pbar)/n)

    center = pbar
    lcl = center - 3*sd
    if lcl < 0:
        lcl = 0
    ucl = center + 3*sd
    if ucl > 1:
        ucl = 1.0
    return center, lcl, ucl


def get_stats_np(data, size):
    n = size
    assert n > 1

    pbar = float(sum(data)) / (n * len(data))
    sd = np.sqrt(n*pbar*(1-pbar))

    center = n*pbar
    lcl = center - 3*sd
    if lcl < 0:
        lcl = 0
    ucl = center + 3*sd
    if ucl > n:
        ucl = n
    return center, lcl, ucl


def get_stats_c(data, size):
    cbar = np.mean(data)

    center = cbar
    lcl = center - 3*np.sqrt(cbar)
    if lcl < 0:
        lcl = 0
    ucl = center + 3*np.sqrt(cbar)
    return center, lcl, ucl


def get_stats_u(data, size):
    n = size
    assert n > 1

    cbar = float(sum(data))/(len(data)*n)

    center = cbar
    lcl = center - 3*np.sqrt(cbar/n)
    if lcl < 0:
        lcl = 0
    ucl = center + 3*np.sqrt(cbar/n)
    return center, lcl, ucl


def get_stats_cusum(data, size):
    """
    Find the data for a cusum graph
    Only returns 0 as the center as the data is moved
    its mean and ucl and lcl are not reported
    """
    return 0, None, None


def prepare_data_none(data, size):
    return data


def prepare_data_x_bar_rs_x(data, size):
    data2 = []
    for xset in data:
        data2.append(np.mean(xset))
    return data2


def prepare_data_x_bar_r_r(data, size):
    data2 = []
    for xset in data:
        data2.append(max(xset) - min(xset))
    return data2


def prepare_data_x_bar_s_s(data, size):
    data2 = []
    for xset in data:
        data2.append(np.std(xset, ddof=1))
    return data2


def prepare_data_x_mr(data, size):
    data2 = [0]
    for i in range(len(data)-1):
        data2.append(abs(data[i] - data[i+1]))
    return data2


def prepare_data_p(data, size):
    data2 = [0]
    for d in data:
        data2.append(float(d)/size)
    return data2


def prepare_data_u(data, size):
    data2 = [0]
    for d in data:
        data2.append(float(d)/size)
    return data2


def prepare_data_cusum(data, size, target=None):
    """
    Prepares the data for a CUSUM graph
    subtracts the mean from each data point
    then calculates the culumative sum of each
    $S_m=\sum_{i=1}^m (x_i-\mu)$
    where $x_i$ is the data point
    $\mu$ is the target value
    if $\mu is not provided the mean of the sample is used
    """
    data2 = []
    if target is None:
        target = np.mean(data)
    for d in data:
        data2.append(float(d) - target)
    data3 = [sum(data2[:i]) for i in range(len(data2)+1)]
    return data3

STATS_FUNCS = {
    CHART_X_BAR_R_X: (get_stats_x_bar_r_x, prepare_data_x_bar_rs_x),
    CHART_X_BAR_R_R: (get_stats_x_bar_r_r, prepare_data_x_bar_r_r),
    CHART_X_BAR_S_X: (get_stats_x_bar_s_x, prepare_data_x_bar_rs_x),
    CHART_X_BAR_S_S: (get_stats_x_bar_s_s, prepare_data_x_bar_s_s),
    CHART_X_MR_X: (get_stats_x_mr_x, prepare_data_none),  ##
    CHART_X_MR_MR: (get_stats_x_mr_mr, prepare_data_x_mr), ##
    CHART_P: (get_stats_p, prepare_data_p),
    CHART_NP: (get_stats_np, prepare_data_none),
    CHART_C: (get_stats_c, prepare_data_none),  ##
    CHART_U: (get_stats_u, prepare_data_u),
    CHART_EWMA: (None, prepare_data_none),
    CHART_CUSUM: (get_stats_cusum, prepare_data_cusum),
    CHART_THREE_WAY: (None, prepare_data_none),
    CHART_TIME_SERIES: (None, prepare_data_none)}

RULES_FUNCS = {
    RULES_1_BEYOND_3SIGMA: (test_beyond_limits, 1),
    RULES_2_OF_3_BEYOND_2SIGMA: (test_beyond_2_sigma, 3),
    RULES_4_OF_5_BEYOND_1SIGMA: (test_beyond_1_sigma, 5),
    RULES_7_ON_ONE_SIDE: (test_violating_runs, 7),
    RULES_8_ON_ONE_SIDE: (test_violating_runs, 8),
    RULES_9_ON_ONE_SIDE: (test_violating_runs, 9),
    RULES_6_TRENDING: (test_trending, 6),
    RULES_14_UP_DOWN: (test_up_down, 14),
    RULES_15_BELOW_1SIGMA: (test_below_1_sigma, 15),
    RULES_8_BEYOND_1SIGMA_BOTH_SIDES: (test_beyond_1_sigma_both_sides, 8)}


# noinspection PyUnresolvedReferences
class Spc(object):
    """
    Main class that provides SPC analysis. It detects SPC rules violations.
    It can draw charts using matplotlib.
    :arguments:
      data
       user data as flat array
    **Usage**
    >>> s = Spc([1, 2, 3, 3, 2, 1, 3, 8], CHART_X_MR_X)
    >>> s.get_stats()
    (2.875, 0.21542553191489322, 5.5345744680851068)
    >>> s.get_violating_points()
    {'1 beyond 3*sigma': [7]}
    >>> s.get_chart()
    >>> s = Spc([1, 2, 3, 3, 2, 1, 3, 8], CHART_CUSUM)
    >>> s.get_stats()
    (0, None, None)
    >>> s.get_violating_points()
    {'7 on one side': [7, 8], '1 beyond 3*sigma': [1, 2, 3, 4, 5, 6, 7, 8]}
    >>> s.get_chart()
    """

    def __init__(self, data, chart_type, rules=RULES_BASIC, stats_custom=None, newdata=None, sizes=None):
        data = data if isinstance(data, list) else list(data)
        self.chart_type = chart_type
        self.rules = rules
        self.stats = []
        if newdata is None:
            newdata = []

        sf, pd = STATS_FUNCS[chart_type]
        if sizes is None:
            if isinstance(data[0], (list, tuple, np.ndarray)):
                size = len(data[0])
            else:
                size = 1
        else:
            size = sizes
        if stats_custom is None and chart_type not in (CHART_EWMA, CHART_THREE_WAY,CHART_TIME_SERIES):
            self.center, self.lcl, self.ucl = sf(data, size)
        elif chart_type not in (CHART_EWMA, CHART_THREE_WAY,CHART_TIME_SERIES):
            self.center, self.lcl, self.ucl = stats_custom
#        else:
#            self.center, self.lcl, self.ucl =  0, 0, 0

        self._data = pd(data + newdata, size)
        self.violating_points = self._find_violating_points()

    def _find_violating_points(self, rules=None):
        if rules is None:
            rules = []
        if len(rules) > 0:
            rs = rules
        else:
            rs = self.rules
        points = {}
        for i in range(len(self._data)):
            for r in rs:
                func, points_num = RULES_FUNCS[r]
                if func is None or i <= points_num - 1:
                    continue
                if func(self._data[i-points_num+1:i+1], self.center, self.lcl, self.ucl):
                    points.setdefault(r, []).append(i)
        return points

    def get_chart(self, legend=True, title=None, index=None):
        """Generate chart using matplotlib."""
        try:
            import matplotlib
        except ImportError:
            raise Exception("matplotlib not installed")
        else:
            import matplotlib.pyplot as plt
            import matplotlib.lines as mlines

        if index is not None and not isinstance(index, list):
            index = list(index)

        plt.figure(figsize=(20, 10))
        ax = plt.subplot(111)

        if index is None:
            plt.plot(self._data, "bo-", ms=5, label='Data')
        else:
            plt.plot(index, self._data, "bo-", ms=5, label='Data')

        title = self.chart_type if title is None else title
        plt.title(title, fontsize=22)  # setting the title for the figure
        if self.center is not None:
            plt.axhline(self.center, color='k', linestyle='-', label='Center (%0.3f)' % self.center)
        if self.ucl is not None:
            plt.axhline(self.ucl, color='r', linestyle='-.', linewidth=4, label='UCL (%0.3f)' % self.ucl)
            plt.axhline(self.center+(self.ucl-self.center)/3, color='r', linestyle=':', linewidth=2, label='UCL (%0.3f)' % self.ucl)
            plt.axhline(self.center+(self.ucl-self.center)*2/3, color='r', linestyle=':', linewidth=2, label='UCL (%0.3f)' % self.ucl)
        if self.lcl is not None:
            plt.axhline(self.lcl, color='r', linestyle='-.', linewidth=4, label='LCL (%0.3f)' % self.lcl)
            plt.axhline(self.center-(self.center-self.lcl)/3, color='r', linestyle=':', linewidth=2, label='UCL (%0.3f)' % self.ucl)
            plt.axhline(self.center-(self.center-self.lcl)*2/3, color='r', linestyle=':', linewidth=2, label='UCL (%0.3f)' % self.ucl)

        if RULES_7_ON_ONE_SIDE in self.violating_points:
            for i in self.violating_points[RULES_7_ON_ONE_SIDE]:
                if index is not None:
                    ax.plot([index[i]], [self._data[i]], "yo", ms=10)
                else:
                    ax.plot([i], [self._data[i]], "yo", ms=10)
            ax.plot([], [], color='yellow', linestyle='', marker='o', ms=10, label='Run of 7')

        if RULES_8_ON_ONE_SIDE in self.violating_points:
            for i in self.violating_points[RULES_8_ON_ONE_SIDE]:
                if index is not None:
                    ax.plot([index[i]], [self._data[i]], "yo", ms=10)
                else:
                    ax.plot([i], [self._data[i]], "yo", ms=10)
            ax.plot([], [], color='yellow', linestyle='', marker='o', ms=10, label='Run of 8')

        if RULES_1_BEYOND_3SIGMA in self.violating_points:
            for i in self.violating_points[RULES_1_BEYOND_3SIGMA]:
                if index is not None:
                    ax.plot([index[i]], [self._data[i]], "ro", ms=10)
                else:
                    ax.plot([i], [self._data[i]], "ro", ms=10)
            ax.plot([], [], color='red', linestyle='', marker='o', ms=10, label='Out of Limits')

        # readability improvements
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.grid(axis='y')
        ylim = plt.ylim()
        plt.ylim((ylim[0]-1, ylim[1]+1))

        legend_output = None
        if legend is True:
            legend_output = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        return ax, legend_output

    def get_violating_points(self):
        """Return points that violates rules of control chart"""
        return self.violating_points

    def get_stats(self):
        """Return basic statistics about data as tuple: (center, LCL, UCL)."""
        return self.center, self.lcl, self.ucl




# In[6]:


def get_chart_with_changepoints(values, spcs, legend=True, title=None, index=None):
    """Generate chart using matplotlib."""
    try:
        import matplotlib
    except ImportError:
        raise Exception("matplotlib not installed")
    else:
        import matplotlib.pyplot as plt
        import matplotlib.lines as mlines

    if index is not None and not isinstance(index, list):
        index = list(index)

    size = len(spcs)
    center = []
    ucl = []
    lcl= []
    data = []
    for i in range(size):
        data += spcs[i]._data


    plt.figure(figsize=(20, 10))
    ax = plt.subplot(111)

    if index is None:
        plt.plot(data, "bo-", ms=5, label='Data')
    else:
        plt.plot(index, data, "bo-", ms=5, label='Data')

    title = spcs[0].chart_type if title is None else title
    plt.title(title, fontsize=22)  # setting the title for the figure


    if spcs[0].center is not None:
        for i in range(size):
            center += [spcs[i].center]*len(spcs[i]._data)
        plt.plot(center, color='k', linestyle='-', label='Center ')

    if spcs[0].ucl is not None:
        for i in range(size):
            ucl += [spcs[i].ucl]*len(spcs[i]._data)
        plt.plot(ucl, color='r', linestyle='-.', label='UCL ')
        plt.plot(np.array(center)+(np.array(ucl)-np.array(center))/3, color='r', linestyle=':', linewidth=2, label='1 Sigma')
        plt.plot(np.array(center)+(np.array(ucl)-np.array(center))*2/3, color='r', linestyle=':', linewidth=2, label='2 Sigma')

    if spcs[0].lcl is not None:
        for i in range(size):
            lcl += [spcs[i].lcl]*len(spcs[i]._data)
        plt.plot(lcl, color='r', linestyle='-.', label='LCL ')
        plt.plot(np.array(center)-(np.array(center)-np.array(lcl))/3, color='r', linestyle=':', linewidth=2, label='1 Sigma')
        plt.plot(np.array(center)-(np.array(center)-np.array(lcl))*2/3, color='r', linestyle=':', linewidth=2, label='2 Sigma')

    start_indx = 0
    legnd = []

    for j in range(size):
        if RULES_7_ON_ONE_SIDE in spcs[j].violating_points:   ######     1
            legnd += [1]
            for i in spcs[j].violating_points[RULES_7_ON_ONE_SIDE]:
                if index is not None:
                    ax.plot([index[i]], [spcs[j]._data[i]], "kD", ms=10)
                else:
                    ax.plot([i+start_indx], [spcs[j]._data[i]], "kD", ms=10)
#            ax.plot([], [], color='black', linestyle='', marker='D', ms=10, label='Run of 7')

        if RULES_8_ON_ONE_SIDE in spcs[j].violating_points:   ######     2
            legnd += [2]
            for i in spcs[j].violating_points[RULES_8_ON_ONE_SIDE]:
                if index is not None:
                    ax.plot([index[i]], [spcs[j]._data[i]], "yo", ms=10)
                else:
                    ax.plot([i+start_indx], [spcs[j]._data[i]], "yo", ms=10)
#            ax.plot([], [], color='yellow', linestyle='', marker='o', ms=10, label='Run of 8')

        if RULES_9_ON_ONE_SIDE in spcs[j].violating_points:   ######     3
            legnd += [3]
            for i in spcs[j].violating_points[RULES_9_ON_ONE_SIDE]:
                if index is not None:
                    ax.plot([index[i]], [spcs[j]._data[i]], "ko", ms=10)
                else:
                    ax.plot([i+start_indx], [spcs[j]._data[i]], "ko", ms=10)
#            ax.plot([], [], color='black', linestyle='', marker='o', ms=10, label='Run of 9')

        if RULES_2_OF_3_BEYOND_2SIGMA in spcs[j].violating_points:   ######     4
            legnd += [4]
            for i in spcs[j].violating_points[RULES_2_OF_3_BEYOND_2SIGMA]:
                if index is not None:
                    ax.plot([index[i]], [spcs[j]._data[i]], "go", ms=10)
                else:
                    ax.plot([i+start_indx], [spcs[j]._data[i]], "go", ms=10)
#            ax.plot([], [], color='green', linestyle='', marker='o', ms=10, label='2 of 3 Beyond 2 Sigma ')

        if RULES_4_OF_5_BEYOND_1SIGMA in spcs[j].violating_points:  ######     5
            legnd += [5]
            for i in spcs[j].violating_points[RULES_4_OF_5_BEYOND_1SIGMA]:
                if index is not None:
                    ax.plot([index[i]], [spcs[j]._data[i]], "co", ms=10)
                else:
                    ax.plot([i+start_indx], [spcs[j]._data[i]], "co", ms=10)
#            ax.plot([], [], color='cyan', linestyle='', marker='o', ms=10, label='4 of 5 Beyond 1 Sigma ')

        if RULES_15_BELOW_1SIGMA in spcs[j].violating_points:  ######     6
            legnd += [6]
            for i in spcs[j].violating_points[RULES_15_BELOW_1SIGMA]:
                if index is not None:
                    ax.plot([index[i]], [spcs[j]._data[i]], "mv", ms=10)
                else:
                    ax.plot([i+start_indx], [spcs[j]._data[i]], "mv", ms=10)
#            ax.plot([], [], color='magenta', linestyle='', marker='v', ms=10, label='15 Below 1 Sigma ')

        if RULES_14_UP_DOWN in spcs[j].violating_points:   ######     7
            legnd += [7]
            for i in spcs[j].violating_points[RULES_14_UP_DOWN]:
                if index is not None:
                    ax.plot([index[i]], [spcs[j]._data[i]], "mo", ms=8)
                else:
                    ax.plot([i+start_indx], [spcs[j]._data[i]], "mo", ms=8)
#            ax.plot([], [], color='magenta', linestyle='', marker='o', ms=8, label='14 Up and Down ')

        if RULES_6_TRENDING in spcs[j].violating_points:  ######     8
            legnd += [8]
            for i in spcs[j].violating_points[RULES_6_TRENDING]:
                if index is not None:
                    ax.plot([index[i]], [spcs[j]._data[i]], "cv", ms=10)
                else:
                    ax.plot([i+start_indx], [spcs[j]._data[i]], "cv", ms=10)
#            ax.plot([], [], color='magenta', linestyle='', marker='v', ms=10, label='6 Trending')


        if RULES_8_BEYOND_1SIGMA_BOTH_SIDES in spcs[j].violating_points:  ######     10
            legnd += [10]
            for i in spcs[j].violating_points[RULES_8_BEYOND_1SIGMA_BOTH_SIDES]:
                if index is not None:
                    ax.plot([index[i]], [spcs[j]._data[i]], "kv", ms=10)
                else:
                    ax.plot([i+start_indx], [spcs[j]._data[i]], "kv", ms=10)
#            ax.plot([], [], color='black', linestyle='', marker='v', ms=10, label='8 Beyond 1 Sigma on Both Sides')

        if RULES_1_BEYOND_3SIGMA in spcs[j].violating_points:   ######     9
            legnd += [9]
            for i in spcs[j].violating_points[RULES_1_BEYOND_3SIGMA]:
                if index is not None:
                    ax.plot([index[i]], [spcs[j]._data[i]], "ro", ms=10)
                else:
                    ax.plot([i+start_indx], [spcs[j]._data[i]], "ro", ms=10)
#            ax.plot([], [], color='red', linestyle='', marker='o', ms=10, label='Out of Limits')

        start_indx += len(spcs[j]._data)

    if 1 in legnd:
        ax.plot([], [], color='black', linestyle='', marker='D', ms=10, label='Run of 7')
    if 2 in legnd:
        ax.plot([], [], color='yellow', linestyle='', marker='o', ms=10, label='Run of 8')
    if 3 in legnd:
        ax.plot([], [], color='black', linestyle='', marker='o', ms=10, label='Run of 9')
    if 4 in legnd:
        ax.plot([], [], color='green', linestyle='', marker='o', ms=10, label='2 of 3 Beyond 2 Sigma ')
    if 5 in legnd:
        ax.plot([], [], color='cyan', linestyle='', marker='o', ms=10, label='4 of 5 Beyond 1 Sigma ')
    if 6 in legnd:
        ax.plot([], [], color='magenta', linestyle='', marker='v', ms=10, label='15 Below 1 Sigma ')
    if 7 in legnd:
        ax.plot([], [], color='magenta', linestyle='', marker='o', ms=8, label='14 Up and Down ')
    if 8 in legnd:
        ax.plot([], [], color='cyan', linestyle='', marker='v', ms=10, label='6 Trending')
    if 9 in legnd:
        ax.plot([], [], color='red', linestyle='', marker='o', ms=10, label='Out of Limits')
    if 10 in legnd:
        ax.plot([], [], color='black', linestyle='', marker='v', ms=10, label='8 Beyond 1 Sigma on Both Sides')


    # readability improvements
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(axis='y')
    ylim = plt.ylim()
    plt.ylim((ylim[0]-1, ylim[1]+1))

    legend_output = None
    if legend is True:
        legend_output = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    return ax, legend_output




def spc_with_changepoints(data, chart_type, change_points, rules=RULES_BASIC, stats_custom=None, newdata=None, sizes=None):

    parts = len(change_points)#+1
#    change_points.append(len(data))
    SPCs = []
    flag = 0
    data = np.array(data)

    for i in range(parts):
        if len(data.shape)>1:
            spc = Spc(data[flag:change_points[i],:], chart_type, rules = rules )
        else:
            spc = Spc(data[flag:change_points[i]], chart_type, rules = rules )
        SPCs.append(spc)
        flag = change_points[i]

    return SPCs


# # DEMO for SPC with Changepoints
#


#
#FUNCS = CHART_X_MR_X
#RULES = RULES_ALL
#
#### change_points listesinde istediğiniz indeksleri sırayla girin, boş bırakırsanız verinin tamamını değerlendirir
#
#change_pnts = []
#
#for i in range(np.array(values).shape[1]):
#
#    spcs = spc_with_changepoints(np.array(values)[:,i], FUNCS, change_points = change_pnts+[len(values)], rules = RULES )
#
#    for j in range(len(change_pnts)+1):
#        if len(spcs[j].violating_points.keys())!=0:
#            print(spcs[j].violating_points)
#
#    get_chart_with_changepoints(np.array(values)[:,i], spcs, legend=True, title=None, index=None)




