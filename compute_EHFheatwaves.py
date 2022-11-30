#!/usr/bin/env python

""" compute_EHFheatwaves.py

Author: Daniel Argueso @ CCRC, UNSW. Sydney (Australia)
email: d.argueso@ unsw.edu.au
Created: Wed Jun 24 11:21:31 AEST 2015 - from compute_EHFheatwaves.py

Yearly maximum heatwave intensity (HWA)
Yearly average heatwave intensity (HWM)
Yearly number of heatwaves        (HWF)
Yearly number of heatwave days    (HWN)
Duration of yearly longest heatwave (HWD)
Timing of the first heatwave      (HWT)
Percentile use to determine extremes (either 90th or 95th depending on the method) (pct)
Array with daily EHF index (EHF)
Temperature equivalent to HWM (HWMt)
Temperature equivalent to HWA (HWAt)
Index containing the number of consecutive heat wave days (spell_all)
Yearly mean duration of heatwaves (HWL)


Script based on Sarah's matlab script EHF_index.m
Script based on D. Argueso compute_EHFheatwaves.py

Created: 09 September 2013
Modified: 15 October 2013
Modified: Tue Jun 23 15:02:54 AEST 2015 - The code has been simplified and made more efficient.
                                          Some options were removed because they were not necessary (NFR09)
                                          and some hardcoded options were incorporated in a better way.
Modified: Fri Jan 29 11:59:12 AEDT 2016 - Added new method to calculate spells using groups
Modified: 2018-07-25 12:34 - Added NH and SH summer options
"""

import netCDF4 as nc
import numpy as np
from constants import const
import glob as glob
from itertools import groupby
import datetime as dt

import pdb


def calc_percentile(tave, nyears, thres_file=None, method="NF13", nwindow=15):

    """Function to calculate the percentile that indentifies hot days
    tave: mean daily temperature calcualted from tmax and tmin
    nyears: number of years in the analysed period
    thres_file: file that contains previously calculated percentiles
    method: now two methods are supported depending on how the percentiles are calculated 'NF13' and 'PA13'
    nwindow: number of days for the window used to calculate percentiles in PA13 method
    ---
    output: pct_calc
    """
    if method == "NF13":

        if thres_file == None:
            print("No thresholds file provided, we will calculate them")

            if not isinstance(tave, np.ma.core.MaskedArray):
                pct_calc = np.percentile(tave, 95, axis=0)

            else:
                pct_calc = np.ones(tave.shape[1:], float) * const.missingval
                for i in range(tave.shape[1]):
                    for j in range(tave.shape[2]):
                        aux = tave[:, i, j]
                        if len(aux[~aux.mask].data) != 0:
                            pct_calc[i, j] = np.percentile(
                                aux[~aux.mask].data, 95, axis=0
                            )
        else:
            print("Percentiles are retrieved from the thfile provided")
            pct_file = nc.Dataset(thres_file, "r")
            pct_calc = pct_file.variables["PRCTILE95"][:].astype("float")

    elif method == "PA13":

        if thres_file == None:
            # No percentile file is provided and thus they are calculated from the given data
            print("Percentiles are calculated because no thfile is provided")
            windowrange = np.zeros((365,), dtype=bool)
            windowrange[: int(np.ceil(nwindow / 2))] = True
            windowrange[-int(np.floor(nwindow / 2)) :] = True
            if np.sum(windowrange) != nwindow:
                raise SystemExit(0)
            windowrange = np.tile(windowrange, nyears)
            pct_calc = np.ones((365,) + tave.shape[1:], float) * const.missingval

            if not isinstance(tave, np.ma.core.MaskedArray):
                for d in range(365):
                    pct_calc[d, :, :] = np.percentile(
                        tave[windowrange == True, :, :], 90, axis=0
                    )
                    windowrange = np.roll(windowrange, 1)

            else:
                for i in range(tave.shape[1]):
                    for j in range(tave.shape[2]):
                        for d in range(365):
                            aux = tave[windowrange == True, :, :]
                            if len(aux[~aux.mask].data) != 0:
                                pct_calc[d, :, :] = np.percentile(
                                    aux[~aux.mask].data, 90, axis=0
                                )
                            windowrange = np.roll(windowrange, 1)

        else:
            print("Percentiles are retrieved from the thfile provided")
            # A percentile file is provided and it contains a PRCTILE90 variable
            pct_file = nc.Dataset(thres_file, "r")
            pct_calc = pct_file.variables["PRCTILE90"][:].astype("float")

    else:
        raise ValueError("Method not supported: Choose between NF13 or PA13")

    return pct_calc


def calc_spell(series):

    if isinstance(series, np.ma.core.MaskedArray):
        if np.any(series.mask == True):
            series[series.mask] = -99

    srun = np.zeros(series.shape)
    srun[1:] = np.diff(series, axis=0)
    srun[srun == 99] = -1
    srun[srun == 100] = 1
    srun[0] = -1
    if isinstance(series, np.ma.core.MaskedArray):
        L = (series.data).tolist()
    else:
        L = (series).tolist()
    groups_hw = []

    for k, g in groupby(L):
        if k == 1:
            b = list(g)
            groups_hw.append(sum(b))

    spell_hw = np.zeros((len(series),), dtype=int)
    if np.any(srun == 1):
        spell_hw[srun == 1] = np.asarray(groups_hw)

    ## Keep only spells equal or larger than 3 days

    spell_hw[spell_hw < 3] = 0
    return spell_hw


def compute_EHF(
    tave,
    dates=None,
    thres_file=None,
    bsyear=None,
    beyear=None,
    month_starty=1,
    mask=None,
    method="NF13",
    nwindow=15,
    EHFaccl=False,
    season="yearly",
):
    """Function to calculate Excess Heat Factor (EHF) heatwaves from tave calcualted as (tmax+tmin)/2."""
    if mask == None:
        mask = np.ones(tave.shape[1:], int)

    # PERFORM SOME CHECKS
    ## This is explicitly checked to preserve compatibility across versions
    if (bsyear == None) or (beyear == None):
        sys.exit(
            "ERROR: you didn't provide base period years to compute_EHF function, please revise"
        )

    years_all = np.asarray([dates[i].year for i in range(len(dates))])
    months_all = np.asarray([dates[i].month for i in range(len(dates))])
    days_all = np.asarray([dates[i].day for i in range(len(dates))])

    # If using PA13, leap days need to be removed

    if method == "PA13":

        dates = dates[((months_all == 2) & (days_all == 29)) == False]
        years = np.asarray([dates[i].year for i in range(len(dates))])
        months = np.asarray([dates[i].month for i in range(len(dates))])
        days = np.asarray([dates[i].day for i in range(len(dates))])

        tave = tave[((months_all == 2) & (days_all == 29)) == False, :, :]

    else:

        years = np.asarray([dates[i].year for i in range(len(dates))])
        months = np.asarray([dates[i].month for i in range(len(dates))])
        days = np.asarray([dates[i].day for i in range(len(dates))])

    # Specify when the year start
    # It is important to define seasons (e.g. Souther Hemisphere, month_starty should be in winter)
    new_years = years.copy()
    new_years[months < month_starty] -= 1

    syear = np.min(years)
    eyear = np.max(years)
    nyears = eyear - syear + 1
    nbyears = beyear - bsyear + 1

    shift_pct = np.argmax(new_years == syear)

    ndays = tave.shape[0]
    nlat = tave.shape[1]
    nlon = tave.shape[2]

    # Calculate percentiles over the base period
    pct = calc_percentile(
        tave[(years >= bsyear) & (years <= beyear), :, :],
        nbyears,
        thres_file,
        method=method,
        nwindow=15,
    )

    tave_3days = np.zeros(tave.shape, dtype=float)

    for t in range(2, ndays):
        tave_3days[t, :, :] = np.mean(tave[t - 2 : t + 1, :, :], axis=0)

    if EHFaccl == True:
        tave_30days = np.zeros(tave.shape, dtype=float)
        for t in range(32, ndays):
            tave_30days[t, :, :] = np.mean(tave[t - 32 : t - 2, :, :], axis=0)

            ###############################################
            ###############################################
            ### CALCULATING EHIsig and EHIaccl (if required)

    if method == "PA13":
        EHIsig = np.zeros(tave.shape, dtype=float)
        for t in range(ndays):
            EHIsig[t, :, :] = tave_3days[t, :, :] - pct[(t) % 365, :, :]
    else:
        EHIsig = tave_3days - pct

    if EHFaccl == True:
        EHIaccl = tave_3days - tave_30days

    ###############################################
    ###############################################
    ## CALCULATING EHF and EHF_Exceed

    if EHFaccl == True:
        EHF = np.maximum(1, EHIaccl) * EHIsig
    else:
        EHF = EHIsig
    EHF[EHF < 0] = 0

    EHF_exceed = np.zeros(EHF.shape, dtype=int)
    EHF_exceed[EHF > 0] = 1

    if EHFaccl == True:
        del tave_30days, EHIaccl, EHIsig

    ###### ZEROING DAYS NOT BELONGING TO SUMMER (SH: NOV,DEC,JAN,FEB,MAR; NH: MAY,JUN,JUL,AUG,SEP)
    ###### Originally used only in PA13 method
    if season == "summer_sh":
        EHF_exceed[(months >= 4) & (months <= 10), :, :] = False
        years[(months >= 4) & (months <= 10)] = -99

        ## For heat wave timing purposes
        shift_start_year = (
            dt.datetime(syear, 11, 0o1) - dt.datetime(syear, 0o7, 0o1)
        ).days

    elif season == "summer_nh":
        EHF_exceed[(months >= 10) | (months <= 4), :, :] = False
        years[(months >= 10) | (months <= 4)] = -99
        shift_start_year = 0

    elif season == "yearly":
        shift_start_year = 0
    else:
        raise ValueError(
            "Season not supported: Choose between summer_sh, summer_nh or yearly"
        )

        # Defining variables for heat wave and spell calculation
    heatwave_EHF_avg = np.ones(tave.shape, dtype=float) * const.missingval
    heatwave_EHF_peak = np.ones(tave.shape, dtype=float) * const.missingval
    heatwave_EHF = np.zeros(tave.shape, dtype=bool)
    spell_all = np.zeros(tave.shape, dtype=int)

    for ilat in range(nlat):
        for ilon in range(nlon):
            if mask[ilat, ilon] == 1:
                spell = calc_spell(EHF_exceed[:, ilat, ilon])

                for t in range(ndays):
                    if spell[t] != 0:
                        heatwave_EHF_avg[t, ilat, ilon] = np.mean(
                            EHF[t : t + spell[t], ilat, ilon]
                        )
                        heatwave_EHF_peak[t, ilat, ilon] = np.max(
                            EHF[t : t + spell[t], ilat, ilon]
                        )
                        heatwave_EHF[t : t + spell[t], ilat, ilon] = EHF_exceed[
                            t : t + spell[t], ilat, ilon
                        ]

                spell_all[:, ilat, ilon] = spell

    ### PULLING OUT HW CHARACTERISTICS

    heatwave_EHF_avg = np.ma.masked_equal(heatwave_EHF_avg, const.missingval)
    heatwave_EHF_peak = np.ma.masked_equal(heatwave_EHF_peak, const.missingval)

    tave_peak_masked = np.ma.masked_where(heatwave_EHF_peak.mask, tave_3days)
    tave_avg_masked = np.ma.masked_where(heatwave_EHF_avg.mask, tave_3days)

    HWA = np.ones((nyears,) + tave.shape[1:], float) * const.missingval
    HWM = np.ones((nyears,) + tave.shape[1:], float) * const.missingval
    HWN = np.ones((nyears,) + tave.shape[1:], float) * const.missingval
    HWF = np.ones((nyears,) + tave.shape[1:], float) * const.missingval
    HWD = np.ones((nyears,) + tave.shape[1:], float) * const.missingval
    HWT = np.ones((nyears,) + tave.shape[1:], float) * const.missingval
    HWMt = np.ones((nyears,) + tave.shape[1:], float) * const.missingval
    HWAt = np.ones((nyears,) + tave.shape[1:], float) * const.missingval
    HWL = np.ones((nyears,) + tave.shape[1:], float) * const.missingval

    for yr in range(nyears):
        year = yr + syear
        HWA[yr, :, :] = np.ma.max(heatwave_EHF_peak[new_years == year, :, :], axis=0)
        HWM[yr, :, :] = np.ma.mean(heatwave_EHF_avg[new_years == year, :, :], axis=0)
        HWF[yr, :, :] = (
            np.sum(spell_all[new_years == year, :, :], axis=0)
            * 100.0
            / float(np.sum(new_years == year))
        )
        HWN[yr, :, :] = np.sum(spell_all[new_years == year, :, :] != 0, axis=0)
        HWD[yr, :, :] = np.max(spell_all[new_years == year, :, :], axis=0)
        HWL[yr, :, :] = (
            np.ma.sum(spell_all[new_years == year, :, :], axis=0) / HWN[yr, :, :]
        )
        HWT[yr, :, :] = np.argmax(spell_all[new_years == year, :, :] != 0, axis=0)

        HWAt[yr, :, :] = (
            np.ma.max(tave_peak_masked[new_years == year, :, :], axis=0) - const.tkelvin
        )
        HWMt[yr, :, :] = (
            np.ma.mean(tave_avg_masked[new_years == year, :, :], axis=0) - const.tkelvin
        )

    HWT = np.ma.masked_equal(HWT, 0.0)
    HWMt[HWMt == 0] = const.missingval
    HWM[HWM == 0] = const.missingval
    HWL[HWN == 0] = const.missingval
    HWA[HWA == 0] = const.missingval
    HWAt[HWAt == 0] = const.missingval

    return HWA, HWM, HWF, HWN, HWD, HWT, pct, EHF, HWMt, HWAt, spell_all, HWL
