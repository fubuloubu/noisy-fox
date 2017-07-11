from basic_file_manager import FileContentManager
from traverse import traverse

import xmltodict

class XMLContentManager(FileContentManager):
    # Override to update representation string
    # Also updates how write() method works
    def __str__(self):
        return xmltodict.unparse(super().__str__(), pretty=True)
    
    # Override to update object parsing
    def _read(self):
        return xmltodict.parse(super()._read())
    
    # XML Methods
    def get(self, path):
        return traverse(self._contents, path)

    def set(self, path, value):
        traverse(self._contents, path, value=value)

if __name__ == '__main__':
    # Run tests
    from os.path import isfile as file_exists
    
    filename = 'test.xml'
    xml = xmltodict.parse('''
    <root>
      <name type="title">
      This is a test
      </name>
      <item>Item 1</item>
      <item>Item 2</item>
      <item attr="a"></item>
      <item attr="b"></item>
    </root>
    ''')
    # Ensure that reading/writing XML parses okay
    obj = XMLContentManager(filename, new_contents=xml)
    obj._write() #TODO: FileContentManager().reference-counting 
    del obj
    assert(file_exists(filename))
    with open(filename, 'r') as f:
        contents = xmltodict.unparse(xml, pretty=True)
        assert(f.read() == contents)
    
    # Ensure getter/setter methods work reasonably well
    obj = XMLContentManager(filename)
    assert(obj.get('root/name/@type') == 'title')
    assert(obj.get('root/name/#text') == 'This is a test')
    assert(len(obj.get('root/item')) == 4)
    assert(len(obj.get('root/item/0:3')) == 3)
    assert(obj.get('root/item/0') == 'Item 1')
    assert(obj.get('root/item/2/@attr') == 'a')
    obj.set('root/cool', {'type':'feeling', 'helpful':'yes'})
    assert(obj.get('root/cool/type') == 'feeling')
    obj.set('root/item/-1', ['Item 5', {'@attr' : 'c'}])
    assert(obj.get('root/item/4') == 'Item 5')
    assert(obj.get('root/item/5/@attr') == 'c')
    
    # Remove testing directory (must be empty)
    obj.delete()
    print("XMLContentManager() test cases pass!")
