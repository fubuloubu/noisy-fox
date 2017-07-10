from file_database import FileDBObject, FileDB
import xmltodict
class XMLDBObject(FileDBObject):
    # Override to update representation string
    # Also updates how write() method works
    def __str__(self):
        return xmltodict.unparse(super().__str__(), pretty=True)
    
    # Override to update object parsing
    def read(self):
        return xmltodict.parse(super().read())
    
    # XML Methods
    def get(self, element_path):
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

    def set(self, element_path, value):
        if element_path:
            keypath = element_path.split('/')
            for key in keypath[:-1]:
                self.contents = self.contents.setdefault(key, {})
            self.contents[keypath[-1]] = value

class XMLDB(FileDB):
    def __init__(self, db_root):
        super().__init__(db_root)
        # Override quantities in parent class
        self.obj_class=XMLDBObject
        self._max_memory=54*1024*1024
        self.ext = '.xml'

if __name__ == '__main__':
    # Run tests
    from os import mkdir, rmdir
    from os.path import isfile as file_exists
    
    test_dir = 'xml_testdb'
    mkdir(test_dir)
    db = XMLDB(test_dir)
    N = 100
    print("Checking object creation")
    files_to_check = {}
    for i in range(N):
        obj = {}
        obj['root'] = {}
        obj['root']['name'] = 'Test {:02d}'.format(i)
        obj['root']['@attr'] = 'title'
        db.add_obj('test-{:02d}'.format(i), obj)
        files_to_check['/test-{:02d}'.format(i)] = xmltodict.unparse(obj)
    for basename, contents in files_to_check.items():
        filename = db.db_root + '/' + basename + db.ext
        #assert(not file_exists(filename))
        #[o.write() for o in db.get_objs(fileglob=basename)]
        assert(file_exists(filename))
        with open(filename, 'r') as f:
            assert(f.read() == contents)
    print("Checking queries...")
    all_query = [lambda o: o.get('root/@attr']) == 'title']
    all_objs = db.query(all_query, db.get_objs())
    assert(len(all_objs) == N)
    
    # Remove testing directory (must be empty)
    rmdir(test_dir)
