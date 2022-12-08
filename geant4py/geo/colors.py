import numpy as np

# G4Color does not work well in python, so define a few colors here.
# TODO: more work is needed to save G4Colors to GDML files...


def white():
    return np.array([1.0, 1.0, 1.0])


def red():
    return np.array([1.0, 0.0, 0.0])


def green():
    return np.array([0.0, 1.0, 0.0])


def blue():
    return np.array([0.0, 0.0, 1.0])


def magenta():
    return np.array([1.0, 0.0, 1.0])


def cyan():
    return np.array([0.0, 1.0, 1.0])


def orange():
    return np.array([1.0, 0.6, 0.0])


def darkGrey():
    return np.array([0.7, 0.7, 0.7])
