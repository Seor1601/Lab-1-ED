import random
import string
import time

from persistence.record_store import RecordStore


letters = string.ascii_letters + string.digits


def random_key(size=12):
    text = ''
    for _ in range(size):
        text += random.choice(letters)
    return text


def run_test(n):
    store = RecordStore(
        data_path='data/bench_' + str(n) + '.log',
        index_path='data/bench_' + str(n) + '.bin',
        auto_save_index=False,
    )
    store.table = store.table.__class__(8)

    keys = []

    start_insert = time.time()
    for i in range(n):
        key = 'bench:' + str(i) + ':' + random_key()
        data = ['Player' + str(i), i]
        store.append_record('score', key, data)
        keys.append(key)
    insert_time = time.time() - start_insert

    start_search = time.time()
    for key in keys:
        store.get(key)
    search_time = time.time() - start_search

    print('Registros:', n)
    print('Tiempo insercion:', round(insert_time, 4), 'seg')
    print('Tiempo busqueda:', round(search_time, 4), 'seg')
    print('Colisiones:', store.table.collisions)
    print('Factor de carga:', round(store.table.load_factor(), 4))
    print('Capacidad final:', store.table.capacity)
    print('-' * 35)


if __name__ == '__main__':
    run_test(1000)
    run_test(5000)
    run_test(20000)
