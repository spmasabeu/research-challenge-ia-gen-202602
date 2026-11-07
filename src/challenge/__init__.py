"""Entorno de razonamiento cuantitativo con unidades (IIC3694, desafío 2026).

Interfaz común del curso::

    from challenge import reward
    reward(prompt, completion) -> float
"""

__all__ = ["reward", "verify"]


def __getattr__(name):
    # Import perezoso: permite `python -m challenge.<módulo>` sin advertencias.
    if name in __all__:
        from challenge import verifier

        return getattr(verifier, name)
    raise AttributeError(name)
