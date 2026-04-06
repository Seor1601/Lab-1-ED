import os
import time
from persistence.record_store import RecordStore


def remove_file(path):
    if os.path.exists(path):
        os.remove(path)


def run_test(n):
    data_path = 'data/test_' + str(n) + '.log'
    index_path = 'data/test_' + str(n) + '.bin'
    remove_file(data_path)
    remove_file(index_path)

    store = RecordStore(data_path, index_path, auto_save_index=False)

    start_insert = time.perf_counter()
    for i in range(n):
        key = 'player:' + str(i)
        data = ['P' + str(i), (i % 10) + 1, i % 500, i % 3000]
        store.append_record('profile', key, data)
    store.save_index()
    end_insert = time.perf_counter()

    start_search = time.perf_counter()
    for i in range(n):
        key = 'player:' + str(i)
        store.get(key)
    end_search = time.perf_counter()

    print('Registros:', n)
    print('Tiempo insercion:', round(end_insert - start_insert, 4), 'segundos')
    print('Tiempo busqueda:', round(end_search - start_search, 4), 'segundos')
    print('Colisiones:', store.table.collisions)
    print('Factor de carga:', round(store.table.load_factor(), 4))
    print('Capacidad final:', store.table.capacity)
    print('-' * 40)


if __name__ == '__main__':
    run_test(1000)
    run_test(5000)
    run_test(20000)
