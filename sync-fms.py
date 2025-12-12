import random
import string
import threading
import time

WORD = "MARUTI"
p_maruti = 0.60  # set probability >= 50%

stop_event = threading.Event()   


def generate_random_string(length=6):
    """Generate a random string of fixed length."""
    if random.random() < p_maruti:
        return WORD
    else:
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def write_to_file(filename, interval):
    """Continuously write data at intervals until stop_event is set."""
    while not stop_event.is_set():
        try:
            with open(filename, 'a') as f:
                random_str = generate_random_string()
                f.write(f"{random_str}\n")
                f.flush()
        except Exception as e:
            print(f"Error writing to {filename}: {e}")

        time.sleep(interval)


def check_occurrence(filename) -> int:
    """Check the occurrence of WORD as standalone lines."""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            return sum(1 for line in lines if line.strip() == WORD)
    except FileNotFoundError:
        return 0


def log_occurrence(log_file, interval):
    """Continuously log occurrences at intervals until stop_event is set."""
    while not stop_event.is_set():
        try:
            occ1 = check_occurrence('file1.txt')
            occ2 = check_occurrence('file2.txt')

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            with open(log_file, 'a') as f:
                f.write(f"[{timestamp}] File1: {occ1}, File2: {occ2}\n")
                f.flush()

        except Exception as e:
            print(f"Error logging: {e}")

        time.sleep(interval)


def main():
    start = time.time()

    for fname in ['file1.txt', 'file2.txt', 'counts.log']:
        open(fname, 'w').close()

    t1 = threading.Thread(target=write_to_file, args=('file1.txt', 1))
    t2 = threading.Thread(target=write_to_file, args=('file2.txt', 2))
    t3 = threading.Thread(target=log_occurrence, args=('counts.log', 3))

    t1.start()
    t2.start()
    t3.start()

    print("File monitoring system started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping file monitoring system...")

        stop_event.set()

        t1.join()
        t2.join()
        t3.join()

        end = time.time()
        print(f"Total Time taken: {end - start:.2f} seconds")
        print("All threads stopped cleanly.")


if __name__ == "__main__":
    main()
