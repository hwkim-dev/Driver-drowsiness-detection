import multiprocessing

def worker(shared_value):
    shared_value.value += 1

if __name__ == '__main__':
    shared_value = multiprocessing.Value('i', 0)
    p1 = multiprocessing.Process(target=worker, args=(shared_value,))
    p2 = multiprocessing.Process(target=worker, args=(shared_value,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print(shared_value.value)