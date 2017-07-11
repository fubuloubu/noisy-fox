# Traverse the tree
def traverse(tree, path, value=None):
    # given path='key0/key1/.../keyN',
    # split into key='key0'
    key_split = path.split('/', 1)
    key = key_split[0]
    # and new_path='ley1'/.../keyN'.
    new_path = key_split[-1]
    # If our tree is a dict
    if isinstance(tree, dict):
        # check if our split did not split further.
        if new_path == path:
            # If yes and we are trying to set
            if value:
                # then set,
                tree[path] = value
                return
            # else return the value at that path.
            return tree[path]
        # If our split did work, continue traversal.
        return traverse(tree[key], new_path, value=value)
    # If our tree is a list
    elif isinstance(tree, list):
        # check if our split did not split further.
        if new_path == path:
            # If yes and we are trying to set
            if value:
                # then set
                if path == '-1':
                    # '-1' marks extension
                    tree.extend(value)
                else:
                    # otherwise just directly set
                    tree[int(path)] = value
                return
            # else return value at that path
            if path.strip('-').isdigit():
                # process a digit normally
                return tree[int(path)]
            else:
                # if non-numerical, attempt parsing as a selector
                [start,end] = [int(s) for s in path.split(':')]
                return tree[start:end]
        # If our split did work, continue traversal.
        return traverse(tree[int(key)], new_path, value=value)
    # If tree is neither dict nor list, 
    # assume it is a value and return it
    return tree

if __name__ == '__main__':
    # run tests
    test_tree = {}
    traverse(test_tree, 'root', value={'nested' : {}})
    assert(False if traverse(test_tree, 'root/nested') else True)
    traverse(test_tree, 'root/nested/multiple', value='times')
    assert(traverse(test_tree, 'root/nested/multiple') == 'times')
    traverse(test_tree, 'root/branch', value=['A', 'B'])
    assert(len(traverse(test_tree, 'root/branch')) == 2)
    assert(traverse(test_tree, 'root/branch/0') == 'A')
    assert(traverse(test_tree, 'root/branch/1') == 'B')
    traverse(test_tree, 'root/new', value={'branch': ['C', 'd'] })
    assert(traverse(test_tree, 'root/new/branch/0') == 'C')
    assert(traverse(test_tree, 'root/new/branch/1') == 'd')
    traverse(test_tree, 'root/new/branch/1', value='D')
    assert(traverse(test_tree, 'root/new/branch/1') == 'D')
    traverse(test_tree, 'root/new/branch/-1', value='E') # appends value
    assert(traverse(test_tree, 'root/new/branch') == ['C', 'D', 'E'])
    traverse(test_tree, 'root/new/branch/-1', value=['F', 'G']) # extends value
    assert(traverse(test_tree, 'root/new/branch/2:5') == ['E', 'F', 'G']) # accepts rangers
    assert(len(traverse(test_tree, 'root/new/branch')) == 5)
    traverse(test_tree, 'root/new', value={'nested': {'inside' : {'another' : 'nested'}}})
    assert(traverse(test_tree, 'root/new/nested')['inside']['another'] == 'nested')
    
    print("traverse() test cases pass!")
