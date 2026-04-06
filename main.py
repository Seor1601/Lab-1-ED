import json
import os
from persistence.hash_table import HashTable


class RecordStore:
    def __init__(self, data_path='data/data.log', index_path='data/index.bin', auto_save_index=True):
        self.data_path = data_path
        self.index_path = index_path
        self.table = HashTable(8)
        self.auto_save_index = auto_save_index
        self._ensure_files()
        self._load_or_rebuild_index()

    def _ensure_files(self):
        folder = os.path.dirname(self.data_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        if not os.path.exists(self.data_path):
            open(self.data_path, 'a', encoding='utf-8').close()

    def _load_or_rebuild_index(self):
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'rb') as file:
                    raw = file.read()
                    if len(raw) > 0:
                        data = json.loads(raw.decode('utf-8'))
                        self.table = HashTable.from_list(data)
                        return
            except Exception:
                pass
        self.rebuild_index()
        self.save_index()

    def save_index(self):
        data = self.table.to_list()
        raw = json.dumps(data).encode('utf-8')
        with open(self.index_path, 'wb') as file:
            file.write(raw)

    def append_record(self, record_type, key, data):
        record = [record_type, key, data]
        with open(self.data_path, 'a+', encoding='utf-8') as file:
            file.seek(0, 2)
            offset = file.tell()
            line = json.dumps(record) + '\n'
            file.write(line)
        self.table.put(key, offset)
        if self.auto_save_index:
            self.save_index()
        return offset

    def read_by_offset(self, offset):
        with open(self.data_path, 'r', encoding='utf-8') as file:
            file.seek(offset)
            line = file.readline()
            if not line:
                return None
            return json.loads(line)

    def get(self, key):
        offset = self.table.get(key)
        if offset is None:
            return None
        return self.read_by_offset(offset)

    def delete(self, key):
        ok = self.table.delete(key)
        if self.auto_save_index:
            self.save_index()
        return ok

    def rebuild_index(self):
        self.table = HashTable(8)
        with open(self.data_path, 'r', encoding='utf-8') as file:
            while True:
                offset = file.tell()
                line = file.readline()
                if not line:
                    break
                line = line.strip()
                if line == '':
                    continue
                try:
                    record = json.loads(line)
                    key = record[1]
                    self.table.put(key, offset)
                except Exception:
                    pass

    def get_all_records(self):
        records = []
        with open(self.data_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line == '':
                    continue
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass
        return records
