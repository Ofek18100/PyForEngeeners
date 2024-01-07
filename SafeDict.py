'''
The safedict is a simple dictionary with the additional functionality of raising an error in the case of trying to insert
a key that is already in the dictionary.
This is good if when create the testers some errors have the same code causing for miscalculation of the error count.
'''

class SafeDict(dict):
    def __setitem__(self, key, value):
        if key not in self:
            dict.__setitem__(self, key, value)
        else:
            raise KeyError("Key already exists - check for duplicate error code or duplicate student id's: " + key)