import threading

threads = []
max_threads = 100

def clear_threads():
    global threads
    for thread in threads:
        thread.join()
    threads = []

def do_thread(target, args:tuple=()):
    while True:
        if len(threads) < max_threads:
            thread = threading.Thread(target=target, args=args)
            thread.start()
            threads.append(thread)
            break
        else:
            clear_threads()