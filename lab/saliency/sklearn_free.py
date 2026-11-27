"""Small metrics without scikit-learn."""
import numpy as np
from scipy.stats import rankdata


def auc(y, p):
    """ROC AUC through the Mann-Whitney U statistic (ties get the average rank)."""
    y = np.asarray(y); r = rankdata(p)
    n1 = y.sum(); n0 = len(y) - n1
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n0 * n1))
