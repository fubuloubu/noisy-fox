from xmltodict import unparse as xml_unparse
class SectionObject(object):
    def __init__(self, name=None):
        assert(name)
        self.set_name(name)
    
    def get_name(self):
        return self.data['@name']
    
    def set_name(self, name):
        self.data['@name'] = name

    def __repr__(self):
        return self.data

    def __str__(self):
        return xml_unparse(self.data, pretty=True, indent='  ')

class TimeseriesPoint(object):
    def __init__(time=None, data=None, time_fmt=None, data_fmt=None):
        assert(time)
        assert(data)
        assert(time_fmt)
        assert(data_fmt)
        self.time = time
        self.data = data
        self.time_fmt = time_fmt
        self.data_fmt = data_fmt

    def __str__(self):
        return (time, data)

    def __repr__(self):
        return { 
            '@time' : format(self.time, self.time_fmt), 
            '@data' : format(self.data, self.data_fmt)
        }

class TimeseriesObject(SectionObject):
    def __init__(self, timeseries=None, sample_time=0.00100, lsb=1.000, \
            time_fmt='.05f', data_fmt='.03f', **data):
        super().__init__(**data)
        assert(timeseries)
        self.set_timeseries(timeseries)
        self.set_sample_time(sample_time)
        self.set_lsb(lsb)
        self.set_time_fmt(time_fmt)
        self.set_data_fmt(data_fmt)

    def set_time_fmt(self, time_fmt):
        self.time_fmt = time_fmt

    def set_data_fmt(self, data_fmt):
        self.data_fmt = data_fmt

    def get_fmts(self):
        return time_fmt, data_fmt

    def get_sample_time(self):
        return self.data['@sample_time']
    
    def set_sample_time(self):
        self.data['@sample_time'] = format(sample_time, self.time_fmt)
    
    def get_lsb(self, new_lsb):
        return self.data['@lsb']
    
    def set_lsb(self, lsb, data_fmt):
        self.data['@lsb'] = format(lsb, self.data_fmt)

    def get_timeseries(self):
        return [pt for pt in self.data['timeseries']]

    def set_timeseries(self, timeseries):
        # Note: Timeseries object is default object. 
        # Perhaps make this extensible for other types? e.g. per-customer
        self.data['timeseries'] = [TimeseriesPoint(*pt, *self.get_fmts()) for pt in timeseries]

class SetupObject(SectionObject):
    def __init__(self, value=None, **data):
        super().__init__(**data)
        assert(value)
        self.set_value(value)

    def get_value(self):
        return self.data['@value']

    def set_value(self, value):
        self.data['@value'] = value

class ActionObject(TimeseriesObject):
    pass
    
class ResultObject(TimeseriesObject):
    pass
    
class VerifyObject(TimeseriesObject):
    def __init__(self, latency=None, variance=None, **data):
        super().__init__(**data)
        assert(latency)
        assert(variance)
        self.set_latency(latency)
        self.set_variance(variance)

    def get_latency(self, latency):
        return self.data['@latency']

    def set_latency(self, latency):
        self.data['@latency'] = format(latency, self.time_fmt)

    def get_variance(self, variance):
        return self.data['@variance']

    def set_variance(self, variance):
        self.data['@variance'] = format(variance, self.data_fmt)


section_classes = {
    'setup' : SetupObject,
    'action' : ActionObject,
    'result' : ResultObject,
    'verify' : VerifyObject
}

if __name__ == '__main__':
    data = {'name' : 'sig-name', 'value' : 1.000, 
            'sample_time' : 0.100, 'lsb' : 0.500, 
            'latency' : 0.300, 'variance' : 0.250,
            'timeseries' : [(0, 0), (1, 1), (2, 2), (3, 3)]
    }
    for section in section_classes.keys():
        section_obj = section_classes[section](**data)
        print(section_obj)
