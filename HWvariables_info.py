

class VariablesInfo(object):

    RAW_SOURCE = {
        'HWA':  { 'Longname'   :  'Peak of the hottest heatwave per year',
                      'units'      :  'degC',
                      'description':  'Peak of the hottest heatwave per year - yearly maximum of each heatwave peak',
                      },
        'HWM':  { 'Longname'   :  'Average magnitude of the yearly heatwave',
                      'units'      :  'degC2',
                      'description':  'Average magnitude of the yearly heatwave - yearly average of heatwave magnitude',
                      },
        'HWN':  { 'Longname'   :  'Number of heatwaves',
                      'units'      :  '',
                      'description':  'Number of heatwaves per year',
                      },
        'HWF':  { 'Longname'   :  'Number of heatwave days',
                      'units'      :  '',
                      'description':  'Number of heatwave days - expressed as the percentage relative to the total number of days',
                      },

        'HWD':  { 'Longname'   :  'Duration of yearly longest heatwave',
                      'units'      :  'days',
                      'description':  'Duration of the longest heatwave per year',
                      },
        'HWT':  { 'Longname'   :  'First heat wave day of the year',
                       'units'      :  'day',
                       'description':  'Time of the first heat wave day of the year from 1st %month%',
                       },
        'HWL':  { 'Longname'   :  'Mean duration of heat waves',
                      'units'      :  'days',
                      'description':  'Mean duration of heat waves',
                      },
        'pct':      { 'Longname'   :  'Percentile 95th',
                      'units'      :  'degC',
                      'description':  'Percentile 95th over the entire base_period',
                      },
        'EHFindex':      { 'Longname'   :  'Excess Heat Factor',
                      'units'      :  'degC2',
                      'description':  'Excess Heat Factor index',
                      },
        'HWAt':  { 'Longname'   :  'Temperature at the peak of the hottest heatwave per year ',
                      'units'      :  'degC',
                      'description':  'Temperature at the peak of the hottest heatwave per year - yearly maximum of each heatwave peak',
                      },
        'HWMt':  { 'Longname'   :  'Average temperature for all yearly heatwave',
                      'units'      :  'degC',
                      'description':  'Average temperature for all yearly heatwave - yearly average of temperature heatwave days',
                      },
        'spell':      { 'Longname'   :  'Length of the heatwave',
                        'units'      :  'days',
                        'description':  'Length of the heatwave in days after the date',
                        },


        }




    def get_var_names(self):
        return self.RAW_SOURCE.keys()

    def get_atts(self, var_name):
        """ get the list of variable attributes
        """
        return self.RAW_SOURCE[var_name].keys()

    def is_supported(self, var_name):

        for raw_type, vnames in self.RAW_SOURCE.items():
            if var_name in vnames.keys():
                return True

        return False

    def get_varatt(self,var_name,attrib):
      return self.RAW_SOURCE[var_name][attrib]

    def get_attdict(self,var_name):
        return self.RAW_SOURCE[var_name]
