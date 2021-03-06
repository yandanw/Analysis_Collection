import h5py
import os
import numpy as np
import matplotlib.pyplot as plt

def modulo_degrees_between_m180_p180(angle_degrees):
    '''
    Inputs:
        angle_degrees: np.array

    Convert arbitrary angle in degrees (any real number) to that between -180
    and +180 degrees.
    '''
    angle_new = angle_degrees % 360.0
    angle_new[angle_new > 180.0] -= 360.0

    return angle_new

def is_between_lo_hi(x, lo, hi):
    '''
    Inputs:
        x: float or nd np.array
        lo: float, lower bound
        hi: float, upper bound
    Returns:
        out: bool nd np.array of same shape as x indicating whether each element is
             between lo and hi
    '''
    out = (x >= lo) * (x < hi)
    return out

def find_contiguous_trues(x):
    '''
    Input:
        x: bool 1d np.array

    Identifies the start locations and lengths of all contiguous chunks of
    True values, separated by one or more False values.
    '''
    starts = []
    lengths = []
    acc_len = 0

    if len(x) == 0:
        return []

    if x[0] == True:
        starts.append(0)
        acc_len += 1

    for i in range(1,len(x)):
        if x[i] == True:
            acc_len += 1
            if x[i-1] == False:
                starts.append(i)
        else:
            if acc_len > 0:
                lengths.append(acc_len)
            acc_len = 0

    # If last value was True, add acc_len to lengths
    if acc_len > 0:
        lengths.append(acc_len)

    assert len(starts) == len(lengths)

    out = list(zip(starts, lengths))

    return out



def analyze_fix_stationary(hdf_path, front_region=[-15,15]):
    #h5f_path = "/Users/yandanwang/Desktop/fix_stationary/20220410_201217.h5"

    ## Import data from h5 file
    h5f = h5py.File(hdf_path, 'r')

    trials = h5f['trials']
    iti = h5f.attrs['iti'] if 'iti' in h5f.attrs.keys() else 2 # if iti was not saved, assume 2 seconds
    stim_duration = h5f.attrs['fix_duration']

    ## for each trial, get...
    for tkey in trials.keys():
        # tkey='000'
        trial = trials[tkey]

        ### 0. Pull out timestamps and theta from trial object
        theta_rad = trial['ft_theta'][()] # raw theta in radians from Fictrac
        theta_rad -= theta_rad[0] # theta in radians relative to the beginning of trial
        theta_deg = np.rad2deg(theta_rad)
        ts = trial['ft_timestamps'] # timestamps in seconds since epoch
        ts -= (ts[0] + iti) # timestamps in seconds relative to the first timestamp of trial
        dt = np.mean(np.diff(ts)) # average width of a time step

        stim_period_mask = is_between_lo_hi(ts, 0, stim_duration)
        ts_stim = ts[stim_period_mask]
        theta_deg_stim = theta_deg[stim_period_mask]

        ### 1. amount of time spent in the front region (param)
        theta_wrapped = modulo_degrees_between_m180_p180(theta_deg_stim)
        in_front_region = is_between_lo_hi(theta_wrapped, \
                                           lo=front_region[0], hi=front_region[1])
        duration_in_front_region = np.sum(in_front_region) * dt # in seconds
        proportion_in_front_region = np.sum(in_front_region) / len(in_front_region)

        print(f'Trial {tkey}: {duration_in_front_region:.2f}s ({proportion_in_front_region * 100:.1f}%) in front')

        ### 1. Quantify successful fixation (defined as >2s of staying within front region)
        true_chunks = find_contiguous_trues(in_front_region)
        fixation_durations = np.asarray([x[1]*dt for x in true_chunks])

        fixation_success = np.any(fixation_durations >= 2)
        max_fixation_duration = np.max(fixation_durations)

        print(f'Trial {tkey}: Fixation success: {fixation_success}')
        print(f'Trial {tkey}: Maximum fixation duration: {max_fixation_duration:.2f}s')


        ### 2. bar's position as a time of function ("theta")



    ## draw histogram of delta from center



    h5f.close()



hdf_path = "/Users/yandanwang/Desktop/fix_stationary_2/20220413_124846.h5"
hdf_path = '/Volumes/Extreme SSD/fix_stationary/20220413_133826.h5'

analyze_fix_stationary(hdf_path, front_region=[-15,15])
