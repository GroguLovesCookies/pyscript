import time


class SortedList:
    def __init__(self):
        self.array = []
        self.iter_index = 0

    @classmethod
    def FromArray(cls, arr):
        created = cls()
        created.array = sorted(arr)
        return created

    @classmethod
    def FromSortedList(cls, arr):
        created = cls()
        created.iter_index = arr.iter_index
        created.array = arr.array[:]
        return created

    def append(self, val):
        if len(self.array) == 0:
            self.array.append(val)
        elif len(self.array) == 1:
            if self.array[0] < val:
                self.array.append(val)
            else:
                self.array.insert(0, val)
        else:
            self.array.insert(self.find_add(val, 0, len(self.array)-1), val)

    def find_add(self, val, low, high):
        if self.array[low] < val < self.array[high]:
            pos = low + (high-low)//2
            if self.array[pos] <= val <= self.array[pos+1]:
                return pos+1
            if self.array[pos-1] <= val <= self.array[pos]:
                return pos
            if self.array[pos] < val:
                return self.find_add(val, pos+1, high)
            if self.array[pos] > val:
                return self.find_add(val, low, pos-1)
        if val <= self.array[low]:
            return low
        else:
            return high+1

    def binary_search(self, low, high, val):
        if low < high and self.array[low] <= val <= self.array[high]:
            pos = low + (high-low)//2
            if self.array[pos] == val:
                return pos
            if self.array[pos] < val:
                return self.binary_search(pos+1, high, val)
            else:
                return self.binary_search(low, pos-1, val)
        if low == high:
            if self.array[low] == val:
                return low
        return -1

    def interpolation_search(self, low, high, val):
        if low < high and self.array[low] <= val <= self.array[high]:
            pos = low + (((-(self.array[low]-val)) * (high - low)) // (self.array[high] - self.array[low]))
            if self.array[pos] == val:
                return pos if pos >= 0 else (len(self) + pos)
            if self.array[pos] < val:
                return self.interpolation_search(pos+1, high, val)
            else:
                return self.interpolation_search(low, pos-1, val)
        if low == high:
            if self.array[low] == val:
                return low if low >= 0 else len(self)-low
        return -1

    def __getitem__(self, item):
        return self.array[item]

    def __setitem__(self, key, value):
        self.array[key] = value

    def __delitem__(self, key):
        del self.array[key]

    def __iter__(self):
        self.iter_index = 0
        return self

    def __next__(self):
        if self.iter_index < len(self.array):
            val = self.array[self.iter_index]
            self.iter_index += 1
            return val
        else:
            raise StopIteration

    def __len__(self):
        return len(self.array)

    def __repr__(self):
        return repr(self.array)

    def clear(self):
        self.array.clear()

    def __copy__(self):
        return SortedList.FromSortedList(self)
