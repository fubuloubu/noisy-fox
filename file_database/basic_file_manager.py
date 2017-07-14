from os import remove as file_remove
from os.path import isfile as file_exists
class FileContentManager(object):
    '''
    Class that takes care of loading and manipulating
    a database object stored in a file
    Contains create, read, write, move and delete methods
    for the representative file.
    The representative file is only written to on object
    removal (from memory), saving unnecessary reads/writes
    until necessary (no longer desire to hold object in memory)
    '''
    def __init__(self, filepath, new_contents=None):
        self._filepath = filepath
        # Allow initializing new file from provided contents
        if file_exists(filepath):
            self._contents = self._read()
        elif new_contents:
            self._contents = new_contents
    
    # Override this to update write() method
    def __str__(self):
        return self._contents

    def __repr__(self):
        return  "{0}('{1}')".format(self.__class__.__name__, self._filepath)
    
    def _read(self):
        with open(self._filepath, 'r') as f:
            return f.read()

    def _write(self):
        if self._filepath:
            with open(self._filepath, 'w') as f:
                # Use str() to show how to
                # write it out of the file
                f.write(str(self))
    
    def update_contents(self, new_contents):
        self._contents = new_contents
        self._write() #TODO: FileDatabase().maintain-references

    def delete(self):
        if file_exists(self._filepath):
            # In case file has loaded but is not
            # saved yet (e.g. file contents in memory)
            file_remove(self._filepath)
        self._filepath = None

    def move(self, new_filepath):
        self.delete()
        self._filepath = new_filepath
        self._write() #TODO: FileDatabase().maintain-references

if __name__ == '__main__':
    # We can create a new file by making a new object with
    # the contents specified
    fname = 'new-file.txt'
    # Ensure the test file doesn't already exist
    if file_exists(fname):
        file_remove(fname)
    contents = 'This is is a new FileContentMananger class!'
    obj = FileContentManager(fname, new_contents=contents)
    # Object doesn't write until told or closed context
    assert(not file_exists(fname))
    obj._write()

    # Updating contents of object doesn't change the file
    obj.update_contents(contents.replace('new', 'renamed'))
    contents = obj._contents #TODO: FileDatabase().maintain-references
    with open(fname, 'r') as f:
        assert(contents == f.read()) # From about write
    contents = obj._contents

    # Moving a file object removes the existing file
    obj.move(fname.replace('new','rename'))
    assert(not file_exists(fname))
    fname = obj._filepath
    #assert(not file_exists(fname)) #TODO: FileDatabase().maintain-references
    
    # When references are zero, file is written
    obj._write() #TODO: FileContentManager().reference-counting
    del obj
    with open(fname, 'r') as f:
        assert(contents == f.read())
    
    # We can also initialize an object from an existing file
    contents = 'This is is an existing FileContentManager()!'
    obj = FileContentManager(fname)
    obj.update_contents(contents)
    obj._write()
    with open(fname, 'r') as f:
        assert(contents == f.read())
    
    # Deleting the object's associated file
    # immediately removes that file
    obj.delete()
    assert(not file_exists(fname))

    # If references are removed, file write does not write file if it was deleted
    obj._write() #TODO: FileContentManager().reference-counting
    del obj
    assert(not file_exists(fname))

    print("FileContentManager() Testing Passed!")
