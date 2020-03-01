#!/usr/bin/python3

import numpy as np
import numpy
from scipy.signal import fftconvolve
from astropy.convolution import convolve_fft


def gaussian_blur(in_array, size):
    # expand in_array to fit edge of kernel
    padded_array = np.pad(in_array, size, 'symmetric')
    # build kernel
    x, y = np.mgrid[-size:size + 1, -size:size + 1]
    g = np.exp(-(x**2 / float(size) + y**2 / float(size)))
    g = (g / g.sum()).astype('Float32')
    #print(padded_array.shape, g.shape)
    #out = convolve2d(np.array(in_array), g, max_missing=0.1)
    out = convolve_fft(padded_array, kernel=g, nan_treatment='interpolate', min_wt=0.4, preserve_nan=True, boundary='wrap', crop=True)
    print(in_array.shape)
    print(out)
    print('-----------------')

    trimmed = out[3:-3, 3:-3]
    print(trimmed)
    return out


if __name__ == "__main__":
    arr = np.array([[np.nan, 2, np.nan, 2, 5], [0, np.nan, 0.4, 9, 10], [11, np.nan, 13, np.nan, 3]])
    arr2 = np.nan_to_num(arr, nan=-999.0)
    convolved = gaussian_blur(arr, 3)