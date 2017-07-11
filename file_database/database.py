from .basic_file_manager import FileContentManager

from glob import iglob as find_file
class FileDatabase(object):
    '''
    Initialize resources for processing a file database in a given root 
    directory folder (which is allowed to be multi-leveled).
    Uses an underlying class for managing file objects.
    To eliminate excessive memory usage, there is a limit to the amount
    of objects this database can hold internally. We will load
    and unload objects from here as a FIFO queue (database index)
    in order to keep relevant things in memory (default is 16KB)

    Provides methods for querying objects, adding new objects, and applying
    functions to objects. This class is meant to be an interface to any
    application using a File Database to manage files as individual records
    '''
    def __init__(self, db_root, obj_class=FileContentManager, ext='txt'):
        # Database root directory and file extension
        self._root = db_root
        self._ext = ext
        
        # Class to use to manage database entries (e.g. files)
        self._obj_class = obj_class 

    def _fullpath_from(self, basename):
        return self._root + '/' + basename + '.' + self._ext

    def _load_obj(self, fullpath):
        return self._obj_class(fullpath)
    
    def add_obj(self, basename, obj_content):
        obj = self._obj_class(self._fullpath_from(basename), \
                new_contents=obj_content)
        obj._write() #TODO: FileContentManager().reference-counting
    
    # Get list of objects based on filename globbing
    def get_objs(self, fileglob='**/*'):
        # Default **/* is any file in folder, recursively
        return map(self._load_obj, \
                find_file(self._fullpath_from(fileglob), recursive=True))

    # Given a query, perform tho query on a given list 
    # of objects and return list of objects that pass the query.
    def query(self, query, objs=None):
        return filter(query, objs if objs else self.get_objs())
    
    # Apply the given function to a given set of objects, 
    # and return a list of their results.
    # If no list of objects, apply to all objects in database
    def apply(self, func, objs=None):
        return [r for r in map(func, objs if objs else self.get_objs())]

if __name__ == '__main__':
    from os import mkdir, rmdir, listdir
    from os.path import isfile as file_exists
    
    test_dir = 'file_testdb'
    mkdir(test_dir)

    # Basic file handing
    db = FileDatabase(test_dir)
    # Initialize N files in test db folder using the database
    N = 1000
    files_to_check = {} # Use this as an external means to keep track of things
    for i in range(N):
        basename = 'new-{:03d}'.format(i)
        contents = 'This is file number {} created by FileDatabase()!\n'.format(i)
        files_to_check[db._fullpath_from(basename)] = contents
        db.add_obj(basename, contents)
    
    # Files don't get written until told
    #assert(len(listdir(test_dir)) == 0) #TODO: FileContentManager().reference-counting
    del db # this should write all the files out
    for fname in files_to_check.keys():
        with open(fname, 'r') as f:
            assert(files_to_check[fname] == f.read())
    
    db = FileDatabase(test_dir) # Restart instance of db
    text_to_add = 'I moved it!\n'
    db.apply(lambda o: o.update_contents(o._contents + text_to_add)) # Append this to everything
    db.apply(lambda o: o.move(o._filepath.replace('new-', 'renamed-')))
    
    # Need to do this as we are modifying the dict in the next loop
    filenames = [f for f in files_to_check.keys()]
    for fname in filenames:
        files_to_check[fname.replace('new-', 'renamed-')] = \
                files_to_check.pop(fname) + text_to_add
    
    # All files are not written until told
    #assert(len(listdir(test_dir)) == 0) #TODO: FileDatabase().maintain-references
    del db # this should write all the files out
    for fname in files_to_check.keys():
        with open(fname, 'r') as f:
            assert(files_to_check[fname] == f.read())
    
    # Query testing
    db = FileDatabase(test_dir)
    assert(len([o for o in db.get_objs()]) == N)
    assert(len([o for o in db.get_objs('renamed-0*')]) == N/10)

    query = lambda o: text_to_add in o._contents
    assert(len([o for o in db.query(query)]) == N)
    
    from re import search as re_search
    query = lambda o: re_search('number [0-9]{1,2} created', o._contents) is not None
    assert(len([o for o in db.query(query)]) == N/10)
    
    query = lambda o: '1' in o._contents or '2' in o._contents
    correct_len = len([i for i in range(N) if '1' in str(i) or '2' in str(i)])
    assert(len([o for o in db.query(query)]) == correct_len)
    
    query = lambda o: '1' in o._contents and '2' in o._contents
    correct_len = len([i for i in range(N) if '1' in str(i) and '2' in str(i)])
    assert(len([o for o in db.query(query)]) == correct_len)
    
    db.apply(lambda o: o.delete()) # Delete all files
    db.apply(lambda o: o._write()) # Write all files (but this shouldn't do anything)
    assert(len(listdir(test_dir)) == 0)
    
    # Remove testing directory (must be empty)
    rmdir(test_dir)
    print("FileDatabase() Testing Passed!")
