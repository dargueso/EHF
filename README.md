# EHF
Python code to calculate Excess Heat Factor and derived heatwave metrics
12/06/2015 Daniel Argüeso @ University of New South Wales
email: d.argueso@unsw.edu.au

This is a Python 3 code to calculate Excess Heat Factor and heatwave metrics on a temperature array (time,lat,lon).

The main function is located in compute_EHFheatwaves.py and is called compute_EHF
You will need to provide:

| Input | Description |
|-----|-----|
|tave|Daily Mean temperature computed from daily tmax and tmin.|
|dates| An list of datetime objects|
|thres_file| [OPTIONAL] A netCDF file with the thresholds used to calculate extreme temperature (95th or 90th percentiles)|
|bsyear| [OPTIONAL] If no thres_file is provided, this is the first year of the reference period to calculate thresholds|
|beyear| [OPTIONAL] If no thres_file is provided, this is the last year of the reference period to calculate thresholds|
|month_starty| [OPTIONAL] Month that we consider the first of the year. For Southern Hemisphere, you may set this to 7 - no summers split|
|mask| [OPTIONAL] Array with mask where EHF wont be calculated. For example, Land-Sea mask|
|method| Choose between Nairn and Fawcett (2013) [NF13] or Perkins and Alexander (2013) [PA13]. Differences in the calculations of percentiles|
|nwindow| For PA13 method, length of the window to calculate the calendar day thresholds. Default 15 days
|EHFaccl| True/False. Whether to use Acclimatization over the previous 30 days. Default False|
|season| Calculate EHF and metrics over particular seasons only. Only NH and SH summer supported. Yearly (no seasons) also supported| 

Outputs are

| Output | Description | Units |
|-----|-----|-----|
|HWA|Peak of the hottest heatwave per year - yearly maximum of each heatwave peak|degC or degC2 (depending on EHFaccl)|
|HWM|Average magnitude of the yearly heatwave - yearly average of heatwave magnitude|degC or degC2 (depending on EHFaccl)
|HWF|Number of heatwave days - expressed as the percentage relative to the total number of days|days|
|HWN|Number of heatwaves per year|hw/year|
|HWD|Duration of the longest heatwave per year|days|
|HWT|Time of the first heat wave day of the year from 1st month of the year|day|
|pct|Percentile 90th or 95th over the entire base_period|degC|
|EHF|Excess Heat Factor index|degC or degC2 (depending on EHFaccl)
|HWMt|Average temperature for all yearly heatwave - yearly average of temperature heatwave days|degC|
|HWAt|Temperature at the peak of the hottest heatwave per year - yearly maximum of each heatwave peak|degC|
|spell_all|Length of the heatwave in days after the date|days|
|HWL|Mean duration of heat waves|days|


*(25/07/2018) NOTE: Now, only the functions are provided. I will update soon a sample script to call them*
