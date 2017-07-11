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
                    ('@uid', random_hash()),
                    ('title', 'Enter a Title'),
                    ('description', 'Enter a Description'),
                    ('setup', {}),
                    ('action', {}),
                    ('result', {}),
                    ('verify', {})
                ])
            }
        }
        new_contents = new_contents if new_contents else test_template
        super().__init__(filename, new_contents=new_contents)

    # Default Testcase Data GET/SET
    def get_uid(self):
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
    def create_signal_obj(self, section, name, datapoints, data_fmt='.03f'):
        sig['@name'] = name
        
        # TODO: Identify additional attributes here
        # Might be per-customer
        time_fmt = '.03f'
        if section in ['']:
            sig['@latency'] = format(0, time_fmt)
            sig['@update-rate'] = format(0, time_fmt)
            sig['@lsb'] = format(0, data_fmt)
            sig['@precision'] = format(0, data_fmt)
        
        fmt = lambda time, data: {'@time' : format(time, time_fmt), '@data' : format(data, data_fmt)}
        # Note: Timeseries object is default object. Perhaps make this extensible for other types?
        # e.g. per-customer
        sig['timeseries'] = [fmt(pt) for pt in datapoints]
        
        return sig

    def get_section_objs(self, section):
        return self.get('root/testcase/' + section)
        return sig_template

    def find_section_obj_idx(self, section, name):
        for i, obj in iter(self.get_section_objs(section)):
            if obj['@name'] == name:
                return i

    def add_section_obj(self, section, name):
        sig = self.create_signal_obj(section, name, datapoints)
        self.set('root/testcase/' + section + '/-1', sig)

    def del_section_obj(self, section, name):
        idx = find_section_obj_idx(section, name)
        self.set('root/testcase/' + section + '/' + idx, 'pop')

    def update_section_obj(self, section, name, datapoints):
        sig = self.create_signal_obj(section, name, datapoints)
        idx = find_section_obj_idx(section, name)
        self.set('root/testcase/' + section + '/' + idx, sig)

if __name__ == '__main__':
    test = TestCaseContentManager('test.xml')
    test._write()
    test.delete()
    print("TestCaseContentManager() Testing Passed!")
