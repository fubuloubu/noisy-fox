from os import remove
#from weakref import finalize
class FileDBObject(object):
    def __init__(self, filepath, new_contents=None):
        self.filepath = filepath
        if new_contents:
            # Allow initializing new file
            # from provided contents
            self.contents = new_contents
        else:
            self.contents = self.read()
        #self._finalizer = finalize(self, self.write)
    
    # Override this to update write() method
    def __str__(self):
        return self.contents

    def __repr__(self):
        return  "{0}('{1}')".format(self.__class__.__name__, self.filepath)
    
    def read(self):
        with open(self.filepath, 'r') as f:
            return f.read()

    def write(self):
        if self.filepath:
            with open(self.filepath, 'w') as f:
                # Use repr() to show how to
                # write it out of the file
                f.write(self.__str__())

    def delete(self):
        remove(self.filepath)
        self.filepath = None

    def move(self, new_filepath):
        self.delete()
        self.filepath = new_filepath

from glob import iglob as find
from sys import getsizeof
class FileDB(object):
    # Initialize resources for processing XML
    # There is a limit to the index queue, we will load
    # and unload objects from here as a FIFO queue
    # in order to keep relevant things in memory (default is 54KB)
    def __init__(self, db_root):
        # Database root directory
        self.db_root = db_root
        # Class to use to manage database entries (e.g. files)
        self.obj_class = FileDBObject
        self.ext = '.txt' # File extension
        # Index routine variables
        self._obj_index = []
        self._max_memory = 54*1024

    def _add_to_queue(self, obj):
        self._obj_index.append(obj)
        # Currently no action if exceeding memory usage
        if getsizeof(self._obj_index) > self._max_memory:
            # Pop oldest entry, not in use
            print("Memory usage is above limit!")
            pass#self._obj_index.pop(0).write()

    def _load_from_queue(self, filelist):
        obj_refs = []
        for filepath in filelist:
            # Check if already loaded
            for obj in self._obj_index:
                if obj.filepath == filepath:
                    obj_refs.append(obj)
                    break
            else:
                # Could not find it, so load it
                obj = self.obj_class(filepath)
                self._add_to_queue(obj)
                obj_refs.append(obj)
        return obj_refs

    def get_objs(self, fileglob='**/*'):
        # Default **/* is any file in folder, recursively
        return self._load_from_queue(find(self.db_root + \
                '/' + fileglob + self.ext, recursive=True))
    
    # Load object into database
    def add_obj(self, filename, obj_content):
        obj = self.obj_class(self.db_root + '/' + \
                filename + self.ext, new_contents=obj_content)
        self._add_to_queue(obj)

    # Given a list of element : value tests (where value is a regex search string)
    # perform those queries on a given list of objects.
    # If the queries are meant to be inclusive, OR the queries together.
    # If the queries are meant to be exclusive, AND the queries together.
    def query(self, queries, objs=None, inclusive=True):
        if not objs:
            # Use all objects
            objs = self.get_objs()
        matching_objs = []
        first = True
        for test_fcn in queries:
            if inclusive or first:
                # If exclusive but first query, populate list
                # inclusive OR between queries
                matching_objs.extend([o for o in objs if test_fcn(o) and o not in matching_objs])
                first = False
            else:
                # After first set of results, ensure all further results
                # are exclusive AND between queries
                matching_objs = [o for o in objs if test_fcn(o) and o in matching_objs]
        return matching_objs

if __name__ == '__main__':
    # Run tests
    from os import mkdir, rmdir
    from os.path import isfile as file_exists
    
    # FileDBObject() testing
    print("Checking object creation/destruction and file write...")
    test_dir = 'file_testdb'
    mkdir(test_dir)
    N = 1000
    files_to_check = {}
    for i in range(N):
        # Initialize N files in test db folder
        # Create and destroy immediately
        fname = '{0}/new-{1:03d}.txt'.format(test_dir, i)
        contents = 'This is test number {0}'.format(i)
        files_to_check[fname] = contents
        obj = FileDBObject(fname, new_contents=contents)
        obj.write() #TODO: Object deletion should be handled in class, remove this
        del obj # This should write out to the file
    
    print("Checking file contents...")
    for fname in files_to_check.keys():
        with open(fname, 'r') as f:
            assert(files_to_check[fname] == f.read())
    
    print("Checking object instantiation from file and methods...")
    obj_list = []
    text_to_add = '\nI added some text!'
    for fname in files_to_check.keys():
        obj = FileDBObject(fname)
        assert(files_to_check[fname] == obj.contents)
        new_fname = fname.replace('new-', 'test-')
        obj.move(new_fname)
        assert(not file_exists(fname))
        assert(not file_exists(new_fname))
        obj.contents          += text_to_add
        files_to_check[fname] += text_to_add
        obj.write()
        assert(file_exists(new_fname))
        with open(new_fname, 'r') as f:
            assert(files_to_check[fname] == f.read())
        obj_list.append(obj)
    
    # FileDB() testing
    print("Checking FileDB() instantiation...")
    db = FileDB(test_dir)
    assert(len(db.get_objs()) == N)
    query = [lambda o: text_to_add in o.contents]
    all_objs = db.query(query, db.get_objs())
    assert(len(all_objs) == N)
    print("Checking FileDB querying and globbing...")
    assert(len(db.get_objs('test-0*')) == N/10)
    from re import search as re_search
    queries = [
        # has 1 digit
        lambda o: re_search('number [0-9]\n',      o.contents) is not None,
        # has 2 digits
        lambda o: re_search('number [0-9][0-9]\n', o.contents) is not None
    ]
    one_tenth_objs = db.query(queries)
    assert(len(one_tenth_objs) == N/10)
    no_objs = db.query(queries, inclusive=False)
    assert(len(no_objs) == 0)
    queries = [
        lambda o: '1' in o.contents,
        lambda o: '2' in o.contents
    ]
    one_or_two_objs = db.query(queries, inclusive=True)
    correct_len = len([i for i in range(N) if '1' in str(i) or '2' in str(i)])
    assert(len(one_or_two_objs) == correct_len)
    one_and_two_objs = db.query(queries, inclusive=False)
    correct_len = len([i for i in range(N) if '1' in str(i) and '2' in str(i)])
    assert(len(one_and_two_objs) == correct_len)
    
    print("Checking object removal...")
    for obj in obj_list:
        fname = obj.filepath
        obj.delete()
        obj.write() # Should do nothing
        assert(not file_exists(fname))
    
    # Remove testing directory (must be empty)
    rmdir(test_dir)
