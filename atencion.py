"""Capa de atención de un transformer, solo con NumPy."""

import numpy as np


def softmax(M):
    raise NotImplementedError


def atencion(Q, K, V, mascara=False):
    raise NotImplementedError


def autoatencion(X, Wq, Wk, Wv, mascara=False):
    raise NotImplementedError


def multicabeza(X, cabezas, Wo, mascara=False):
    raise NotImplementedError


def layer_norm(x, eps=1e-5):
    raise NotImplementedError
