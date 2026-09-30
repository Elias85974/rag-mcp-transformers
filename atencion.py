"""Capa de atención de un transformer, solo con NumPy."""

import numpy as np


def softmax(M):
    """Softmax sobre el último eje; restar el máximo evita desbordes sin cambiar el resultado."""
    e = np.exp(M - M.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def atencion(Q, K, V, mascara=False):
    """Atención escalada: A = softmax(Q K^T / sqrt(d_k)), salida = A V. Devuelve (salida, A)."""
    puntajes = Q @ K.T / np.sqrt(K.shape[-1])
    if mascara:
        futuras = np.triu(np.ones(puntajes.shape, dtype=bool), k=1)
        puntajes = np.where(futuras, -np.inf, puntajes)
    A = softmax(puntajes)
    return A @ V, A


def autoatencion(X, Wq, Wk, Wv, mascara=False):
    """Q, K y V salen de la misma secuencia X."""
    return atencion(X @ Wq, X @ Wk, X @ Wv, mascara)


def multicabeza(X, cabezas, Wo, mascara=False):
    """Concatena la salida de cada cabeza (Wq, Wk, Wv) y la proyecta con Wo."""
    salidas = [autoatencion(X, Wq, Wk, Wv, mascara)[0] for Wq, Wk, Wv in cabezas]
    return np.concatenate(salidas, axis=-1) @ Wo


def layer_norm(x, eps=1e-5):
    """Normaliza cada fila a media 0 y varianza 1."""
    media = x.mean(axis=-1, keepdims=True)
    varianza = x.var(axis=-1, keepdims=True)
    return (x - media) / np.sqrt(varianza + eps)
