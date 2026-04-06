class HashEntry:
    def __init__(self, key, value_ref):
        self.key = key
        self.value_ref = value_ref


class HashTable:
    def __init__(self, capacity=8):
        self.capacity = capacity
        self.size = 0
        self.buckets = []
        self.collisions = 0
        for _ in range(capacity):
            self.buckets.append([])
    
    def _hash(self, key):
        total = 0
        for ch in key:
            total = total * 31 + ord(ch)
        if total < 0:
            total = -total
        return total % self.capacity

    def _find_index(self, bucket, key):
        for i in range(len(bucket)):
            if bucket[i].key == key:
                return i
        return -1

    def put(self, key, value_ref):
        index = self._hash(key)
        bucket = self.buckets[index]
        pos = self._find_index(bucket, key)

        if pos != -1:
            bucket[pos].value_ref = value_ref
            return

        if len(bucket) > 0:
            self.collisions += 1

        bucket.append(HashEntry(key, value_ref))
        self.size += 1

        if self.load_factor() > 0.7:
            self.rehash()

    def get(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        pos = self._find_index(bucket, key)
        if pos == -1:
            return None
        return bucket[pos].value_ref

    def delete(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        pos = self._find_index(bucket, key)
        if pos == -1:
            return False
        bucket.pop(pos)
        self.size -= 1
        return True

    def load_factor(self):
        return self.size / self.capacity

    def items(self):
        values = []
        for bucket in self.buckets:
            for entry in bucket:
                values.append((entry.key, entry.value_ref))
        return values

    def rehash(self):
        old_items = self.items()
        self.capacity = self.capacity * 2
        self.size = 0
        self.buckets = []
        for _ in range(self.capacity):
            self.buckets.append([])

        for key, value_ref in old_items:
            index = self._hash(key)
            bucket = self.buckets[index]
            if len(bucket) > 0:
                self.collisions += 1
            bucket.append(HashEntry(key, value_ref))
            self.size += 1

    def to_list(self):
        data = []
        for bucket in self.buckets:
            one_bucket = []
            for entry in bucket:
                one_bucket.append([entry.key, entry.value_ref])
            data.append(one_bucket)
        return data

    @classmethod
    def from_list(cls, data):
        table = cls(len(data))
        table.buckets = []
        table.size = 0
        for bucket_data in data:
            bucket = []
            for pair in bucket_data:
                bucket.append(HashEntry(pair[0], pair[1]))
                table.size += 1
            table.buckets.append(bucket)
        return table
