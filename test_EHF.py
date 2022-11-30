import pytest
import xarray as xr
import pandas as pd
import datetime as dt
from constants import const
from compute_EHFheatwaves import compute_EHF


def test_EHF():

    fin = xr.open_dataset("./test.nc")
    fout_index = xr.open_dataset("./testout_index.nc")

    tave = fin.tas.values
    dt64 = fin.time.values
    dates = pd.to_datetime(dt64)

    (
        HWA,
        HWM,
        HWF,
        HWN,
        HWD,
        HWT,
        pctcalc,
        EHFindex,
        HWMt,
        HWAt,
        spell,
        HWL,
    ) = compute_EHF(
        tave,
        dates,
        thres_file=None,
        bsyear=1989,
        beyear=1999,
        EHFaccl=True,
        method="PA13",
    )

    assert (EHFindex == fout_index.EHF.values).all()


def test_HWA():

    fin = xr.open_dataset("./test.nc")
    fout_metrics = xr.open_dataset("./testout_metrics.nc")

    tave = fin.tas.values
    dt64 = fin.time.values
    dates = pd.to_datetime(dt64)

    (
        HWA,
        HWM,
        HWF,
        HWN,
        HWD,
        HWT,
        pctcalc,
        EHFindex,
        HWMt,
        HWAt,
        spell,
        HWL,
    ) = compute_EHF(
        tave,
        dates,
        thres_file=None,
        bsyear=1989,
        beyear=1999,
        EHFaccl=True,
        method="PA13",
    )

    assert (HWA == fout_metrics.HWA).all()
