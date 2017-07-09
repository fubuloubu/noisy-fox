from os import remove
class FileDBObject(object):
    def __init__(self, filepath, new_contents=None):
        self.filepath = filepath
        if new_contents:
            # Allow initializing new file
            # from provided contents
            self.contents = new_contents
        else:
            self.contents = self.read()
    
    # Override this to update write() method
    def __repr__(self):
        return self.contents

    def __str__(self):
        return  "{0}('{1}')".format(self.__class__, self.filepath)
    
    def read(self):
        with open(self.filepath, 'r') as f:
            return f.read()

    def write(self):
        if self.filepath:
            with open(self.filepath, 'w') as f:
                # Use repr() to show how to
                # write it out of the file
                f.write(self.__repr__())

    def delete(self):
        remove(self.filepath)
        self.filepath = None

    def move(self, new_filepath):
        self.delete()
        self.filepath = new_filepath

    def __del__(self):
        # Write to file so we don't lose data
        self.write()

from glob import iglob as find
from sys import getsizeof
class FileDB(object):
    # Initialize resources for processing XML
    # There is a limit to the index queue, we will load
    # and unload objects from here as a FIFO queue
    # in order to keep relevant things in memory (default is 54KB)
    def __init__(self, db_root, \
            obj_class=FileDBObject, \
            max_memory=54*1024):
        self.db_root = db_root
        self.obj_class = obj_class
        self._obj_index = []
        self._max_memory = max_memory

    def _add_to_queue(self, obj):
        self._obj_index.append(obj)
        # Currently no action if exceeding memory usage
        if getsizeof(self._obj_index) > self._max_memory:
            # Pop oldest entry, not in use
            print("Memory usage is above limit!")
            pass#self._obj_index.pop(0)

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

    def get_objs(self, fileglob='**/*', ext='.txt'):
        # Default **/* is any file in folder, recursively
        return self._load_from_queue(find(self.db_root + \
                '/' + fileglob + ext, recursive=True))

    # Given a list of element : value tests (where value is a regex search string)
    # perform those queries on a given list of objects.
    # If the queries are meant to be inclusive, OR the queries together.
    # If the queries are meant to be exclusive, AND the queries together.
    def query(self, queries, objs, inclusive=True):
        if not objs:
            # Use all objects
            objs = self.get_filetrees()
        matching_objs = []
        first = True
        for test_obj in queries:
            if inclusive or first:
                # If exclusive but first query, populate list
                # inclusive OR between queries
                matching_objs.extend([o for o in objs if test_obj(o)])
            else:
                # After first set of results, ensure all further results
                # are exclusive AND between queries
                first = False
                matching_objs = [o for o in objs if test_obj(o) and o in matching_objs]
        return matching_objs

if __name__ == '__main__':
    # Run tests
    test_dir = 'file_testdb'
    from os import mkdir
    from shutil import rmtree
    try:
        rmtree(test_dir, ignore_errors=True)
    finally:
        mkdir(test_dir)
    N = 1000
    for i in range(N):
        # Initialize N files in test db folder
        # Create and destroy immediately
        print(FileDBObject('{0}/test-{1:03d}.txt'.format(test_dir, i), \
                new_contents='This is test number {0}'.format(i)))


