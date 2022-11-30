#!/usr/bin/env python
"""
@File    :  sample_run_EHF.py
@Time    :  2022/11/30 20:53:04
@Author  :  Daniel Argüeso
@Version :  1.0
@Contact :  d.argueso@uib.es
@License :  (C)Copyright 2022, Daniel Argüeso
@Project :  None
@Desc    :  None
"""


import xarray as xr
from constants import const
import HWvariables_info as hwv
from compute_EHFheatwaves import compute_EHF
import datetime as dt
import pandas as pd
import numpy as np
from cftime import DatetimeNoLeap


version = "PA13"

syear = 1989
eyear = 2008
nyears = eyear - syear + 1

fin = xr.open_dataset("./test.nc")

tave = fin.tas.values
dt64 = fin.time.values
dates = pd.to_datetime(dt64)


HWA, HWM, HWF, HWN, HWD, HWT, pctcalc, EHFindex, HWMt, HWAt, spell, HWL = compute_EHF(
    tave,
    dates,
    thres_file=None,
    bsyear=1989,
    beyear=1999,
    EHFaccl=True,
    method=version,
)


dyear = [dt.datetime(syear + x, 6, 1, 0) for x in range(0, nyears)]
fout = xr.Dataset(
    {
        "HWA": (
            ["year", "y", "x"],
            HWA,
            (
                {
                    "units": "K2",
                    "long_name": "Peak of the hottest heatwave per year",
                    "_FillValue": 1e20,
                    "missing_value": 1e20,
                }
            ),
        ),
        "HWM": (
            ["year", "y", "x"],
            HWM,
            (
                {
                    "units": "K2",
                    "long_name": "Average magnitude of the yearly heatwave",
                    "_FillValue": 1e20,
                    "missing_value": 1e20,
                }
            ),
        ),
        "HWF": (
            ["year", "y", "x"],
            HWF,
            (
                {
                    "units": "days",
                    "long_name": "Number of heatwave days",
                    "_FillValue": 1e20,
                    "missing_value": 1e20,
                }
            ),
        ),
        "HWD": (
            ["year", "y", "x"],
            HWD,
            (
                {
                    "units": "days",
                    "long_name": "Duration of yearly longest heatwave",
                    "_FillValue": 1e20,
                    "missing_value": 1e20,
                }
            ),
        ),
        "HWT": (
            ["year", "y", "x"],
            HWT,
            (
                {
                    "units": "day",
                    "long_name": "First heat wave day of the year",
                    "_FillValue": 1e20,
                    "missing_value": 1e20,
                }
            ),
        ),
        "HWL": (
            ["year", "y", "x"],
            HWL,
            (
                {
                    "units": "days",
                    "long_name": "Mean duration of heat waves",
                    "_FillValue": 1e20,
                    "missing_value": 1e20,
                }
            ),
        ),
        "HWAt": (
            ["year", "y", "x"],
            HWAt,
            (
                {
                    "units": "K",
                    "long_name": "Temperature at the peak of the hottest heatwave per year",
                    "_FillValue": 1e20,
                    "missing_value": 1e20,
                }
            ),
        ),
        "HWMt": (
            ["year", "y", "x"],
            HWMt,
            (
                {
                    "units": "K",
                    "long_name": "Average temperature for all year heatwaves",
                    "_FillValue": 1e20,
                    "missing_value": 1e20,
                }
            ),
        ),
        "lat": (["y", "x"], fin.lat.values.squeeze()),
        "lon": (["y", "x"], fin.lon.values.squeeze()),
    },
    coords={"year": dyear},
)

fout.to_netcdf("./testout_metrics.nc", mode="w")


if version == "PA13":
    dates = [item for item in dates if not (item.month == 2 and item.day == 29)]
    dates = [DatetimeNoLeap(x.year, x.month, x.day) for x in dates]

    with xr.set_options(enable_cftimeindex=True):
        fout_day = xr.Dataset(
            {
                "EHF": (
                    ["time", "y", "x"],
                    EHFindex,
                    (
                        {
                            "units": "K2",
                            "long_name": "Excessive Heat Factor Index",
                            "_FillValue": 1e20,
                            "missing_value": 1e20,
                        }
                    ),
                ),
                "lat": (["y", "x"], fin.lat.values.squeeze()),
                "lon": (["y", "x"], fin.lon.values.squeeze()),
            },
            coords={"time": dates},
        )

        fout_day.to_netcdf("./testout_index.nc", mode="w")
else:

    fout_day = xr.Dataset(
        {
            "EHF": (
                ["time", "y", "x"],
                EHFindex,
                (
                    {
                        "units": "K2",
                        "long_name": "Excessive Heat Factor Index",
                        "_FillValue": 1e20,
                        "missing_value": 1e20,
                    }
                ),
            ),
            "lat": (["y", "x"], fin.lat.values.squeeze()),
            "lon": (["y", "x"], fin.lon.values.squeeze()),
        },
        coords={"time": dates},
    )

    fout_day.to_netcdf("./testout_index.nc", mode="w")
