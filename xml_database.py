from file_database import FileDBObject, FileDB
import xmltodict
class XMLDBObject(FileDBObject):
    # Override to update representation string
    # Also updates how write() method works
    def __repr__(self):
        return xmltodict.unparse(super().__repr__(), pretty=True)
    
    # Override to update object parsing
    def read(self):
        return xmltodict.parse(super().read())
    
    # XML Methods
    def get_value(self, element_path):
        if element_path:
            try:
                xmltree = self.contents.copy()
                keypath = element_path.split('/')
                for key in keypath[:-1]:
                    xmltree = xmltree.setdefault(key, {})
                return xmltree[keypath[-1]]
            except KeyError as error:
                raise Warning("Key not found {}".format(error))
                return None

    def get_attribute(self, element_path, attribute_name):
        return self.get_element(element_path)['@' + attribute_name]

    def set_value(self, element_path, value):
        if element_path:
            keypath = element_path.split('/')
            for key in keypath[:-1]:
                self.contents = self.contents.setdefault(key, {})
            self.contents[keypath[-1]] = value

    def set_attribute(self, element_path, attribute_name, value):
        self.get_element(element_path)['@' + attribute_name] = value

from re import search as re_search
class XMLDB(FileDB):
    # Override to update the memory we can use and provide XML Object
    def __init__(self, db_root):
        max_memory=54*1024*1024 #bytes
        obj_class=XMLDBObject, max_memory=max_memory
        super().__init__(db_root, obj_class=obj_class, max_memory=max_memory)
    
    # Override for extension
    def get_objs(self, fileglob='**/*', ext='.xml'):
        super().get_objs(fileglob=fileglob, ext=ext)
    
    # Override for XML specific queries for a given list of element : value tests
    # (where value is a regex search string)
    def query(self, element_value_tests, objs, inclusive=True):
        # Construct list of query functions for XML Object
        queries = []
        for search_name, match_value in element_value_tests.items():
            queries.append(lambda o: re_search(match_value, \
                    o.get_value(search_name)) is not None)
        # Then pass to super class method
        return super().query(queries, objs, inclusive=inclusive)
