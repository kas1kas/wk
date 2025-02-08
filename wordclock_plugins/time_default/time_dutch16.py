class time_dutch:
    """
    This class returns a given time as a range of LED-indices.
    Illuminating these LEDs represents the current time on a dutch WCA 16x16

             HET IS
    minutes
             VIJF OVER
             TIEN OVER
             KWART OVER
             TIEN VOOR HALF
             VIJF VOOR HALF
             HALF
             VIJF OVER HALF
             TIEN OVER HALF
             KWART VOOR
             TIEN VOOR
             VIJF VOOR
    hours    TWAALF
             EEN
             TWEE
             DRIE
             VIER
             VIJF
             ZES
             ZEVEN
             ACHT
             NEGEN
             TIEN
             ELF
             TWAALF
    full_hour
    """

    def __init__(self):
        self.prefix = list(range(51,54)) +  list(range(55,57))
        self.minutes=[[], \
          list(range(58,62)) + list(range(106,110)), \
          list(range(67,71)) + list(range(106,110)), \
          list(range(89,94)) + list(range(106,110)), \
          list(range(67,71)) + list(range(74,78)) + list(range(99,103)), \
          list(range(58,62)) + list(range(74,78)) + list(range(99,103)), \
          list(range(99,103)), \
          list(range(58,62)) + list(range(83,87)) + list(range(99,103)), \
          list(range(67,71)) + list(range(83,87)) + list(range(99,103)), \
          list(range(89,94)) + list(range(115,119)), \
          list(range(67,71)) + list(range(115,119)), \
          list(range(58,62)) + list(range(115,119)) ]
        self.hours= [list(range(195,201)), \
          list(range(122,125)), \
          list(range(131,135)), \
          list(range(138,142)), \
          list(range(147,151)), \
          list(range(151,155)), \
          list(range(155,158)), \
          list(range(163,168)), \
          list(range(179,183)), \
          list(range(169,174)), \
          list(range(182,186)), \
          list(range(187,190)), \
          list(range(195,201))]
        self.full_hour= list(range(203,206))

    def get_time(self, time, purist):
        hour=time.hour%12+(1 if time.minute//5 > 3 else 0)
        minute=time.minute//5
        # Assemble indices
        return  \
            (self.prefix if not purist else []) + \
            self.minutes[minute] + \
            self.hours[hour] + \
            (self.full_hour if (minute == 0) else [])

