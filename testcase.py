from file_database.xml_file_manager import XMLContentManager

from collections import OrderedDict
from uuid import uuid1 as random_hash

class TestCaseContentManager(XMLContentManager):

    def __init__(self, filename, new_contents=None):
        # Basic template for testcase
        # Note: Use OrderedDict here so we retain the right order in XML
        test_template = {
            'root' : {
                'testcase' : OrderedDict([
                    # So we have a trackable UID that never updates
                    # in case there is every confusion based on named changes, etc.
                    ('@uid', random_hash()), 
                    ('title', 'Enter a Title'),
                    ('description', 'Enter a Description')
                ])
            }
        }
        new_contents = new_contents if new_contents else test_template
        super().__init__(filename, new_contents=new_contents)

    # Default Testcase Data GET/SET
    def get_uid(self): # Note: no setter, should not be updated!
        return self.get('root/testcase/@uid')

    def get_title(self):
        return self.get('root/testcase/title')
    def set_title(self, new_title):
        self.set('root/testcase/title', new_title)

    def get_description(self):
        return self.get('root/testcase/description')
    def set_description(self, new_description):
        self.set('root/testcase/description', new_description)

    # Testcase sectional data GET/SET
    def create_signal_obj(self, section, name, \
            value=0.00000, timeseries=None, \
            latency=0.00000, sample_time=0.00100, \
            lsb=1.000, variance=0.000, \
            time_fmt = '.05f', data_fmt='.03f'):
        
        # Name is required, no matter what
        sig = {}
        sig['@name'] = name
        
        # Depending on the section we're talking about,
        # different attributes apply
        # Note: Attributes might be per-customer
        if section in ['action', 'result', 'verify']:
            sig['@sample_time'] = format(sample_time, time_fmt)
            sig['@lsb'] = format(lsb, data_fmt)
        if section in ['verify']:
            sig['@latency'] = format(latency, time_fmt)
            sig['@variance'] = format(variance, data_fmt)
        
        # The value of the signal is either a timeseries
        if section in ['action', 'result', 'verify']:
            # Note: Timeseries object is default object. 
            # Perhaps make this extensible for other types? e.g. per-customer
            fmt = lambda time, data: { 
                    '@time' : format(time, time_fmt), 
                    '@data' : format(data, data_fmt)
            }
            sig['timeseries'] = [fmt(t,d) for t,d in timeseries]
        # or a static value
        elif section in ['setup']:
            sig['@value'] = format(value, data_fmt)
        
        #else: This should be an appliation error

        return sig

    def get_section_objs(self, section):
        return self.get('root/testcase/' + section)

    def find_section_obj_idx(self, section, name):
        for i, obj in enumerate(self.get_section_objs(section)):
            if obj['@name'] == name:
                return i

    def add_section_obj(self, section, name, data):
        sig = self.create_signal_obj(section, name, **data)
        self.set('root/testcase/' + section + '/-1', sig)

    def del_section_obj(self, section, name):
        idx = str(self.find_section_obj_idx(section, name))
        self.get('root/testcase/' + section + '/' + idx + '/#pop')

    def update_section_obj(self, section, name, data):
        sig = self.create_signal_obj(section, name, **data)
        idx = str(self.find_section_obj_idx(section, name))
        self.set('root/testcase/' + section + '/' + idx, sig)

if __name__ == '__main__':
    # Test this class
    test = TestCaseContentManager('test.xml')
    uid = str(test.get_uid())
    assert(len(uid) != 0)
    new_title = test.get_title() + uid
    test.set_title(new_title)
    assert(test.get_title() == new_title)
    new_description = test.get_description() + uid
    test.set_description(new_description)
    assert(test.get_description() == new_description)
    
    signame1 = 'sig-name-1'
    signame2 = 'sig-name-2'
    data1 = {'value' : 1.000, 'sample_time' : 0.100, 'lsb' : 0.500, 
            'latency' : 0.300, 'variance' : 0.250,
            'timeseries' : [(0, 0), (1, 1), (2, 2), (3, 3)]
    }
    data2 = {'value' : 2.000, 'sample_time' : 0.200, 'lsb' : 1.000, 
            'latency' : 0.400, 'variance' : 0.500,
            'timeseries' : [(0, 1), (1, 2), (2, 3), (3, 4)]
    }
    
    for section in ['setup', 'action', 'result', 'verify']:
        test.add_section_obj(section, signame1, data1)
        idx = test.find_section_obj_idx(section, signame1)
        assert(idx == 0)
        assert(test.get_section_objs(section)[idx]['@name'] == signame1)
        obj = test.get_section_objs(section)[idx]
        for key in obj.keys():
            if key[0] == '@' and key != '@name':
                assert(float(obj[key]) == data1[key.strip('@')])
            if key == 'timeseries':
                for i, pt in enumerate(data1[key]):
                    assert(float(obj[key][i]['@time']) == pt[0])
                    assert(float(obj[key][i]['@data']) == pt[1])
        test.update_section_obj(section, signame1, data2)
        obj = test.get_section_objs(section)[idx]
        for key in obj.keys():
            if key[0] == '@' and key != '@name':
                assert(float(obj[key]) == data2[key.strip('@')])
            if key == 'timeseries':
                for i, pt in enumerate(data2[key]):
                    assert(float(obj[key][i]['@time']) == pt[0])
                    assert(float(obj[key][i]['@data']) == pt[1])
        test.add_section_obj(section, signame2, data1)
        idx = test.find_section_obj_idx(section, signame2)
        assert(idx == 1)
        assert(test.get_section_objs(section)[idx]['@name'] == signame2)
        obj = test.get_section_objs(section)[idx]
        for key in obj.keys():
            if key[0] == '@' and key != '@name':
                assert(float(obj[key]) == data1[key.strip('@')])
            if key == 'timeseries':
                for i, pt in enumerate(data1[key]):
                    assert(float(obj[key][i]['@time']) == pt[0])
                    assert(float(obj[key][i]['@data']) == pt[1])
        test.del_section_obj(section, signame2)
        test.del_section_obj(section, signame1)
        assert(len(test.get_section_objs(section)) == 0)
    
    # Completed testing
    test.delete()
    print("TestCaseContentManager() Testing Passed!")
