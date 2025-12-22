import asyncio
import time
import random
import string
import aiofiles
import sys

WORD = "MARUTI"
p_maruti = 0.62  # probability for MARUTI

def generate_random_string():
    """Generate a random string of fixed length or return WORD based on probability."""
    if random.random() < p_maruti:
        return WORD
    return "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 10)))

async def write_to_file(filename, interval):
    """Asynchronously write data to a file at regular intervals."""
    try:
        while True:
            random_str = generate_random_string()
            async with aiofiles.open(filename, 'a') as f:
                await f.write(f"{random_str}\n")
            # small console heartbeat so we know the writer is alive
            print(f"[{time.strftime('%H:%M:%S')}] wrote to {filename}: {random_str}")
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        print(f"Writer task for {filename} cancelled.")
        raise

async def check_occurrence(filename) -> int:
    """Return count of exact WORD occurrences in the file."""
    try:
        async with aiofiles.open(filename, 'r') as f:
            content = await f.read()
            if not content:
                return 0
            lines = content.strip().splitlines()
            count = sum(1 for line in lines if line.strip() == WORD)
            return count
    except FileNotFoundError:
        return 0
    except Exception as e:
        print(f"Error reading {filename}: {e}", file=sys.stderr)
        return 0

async def log_occurrence(log_file, interval=3):
    """Periodically check both files and append counts to log_file."""
    try:
        while True:
            occ1, occ2 = await asyncio.gather(
                check_occurrence('file1.txt'),
                check_occurrence('file2.txt')
            )
            timestamp = time.strftime("%Y-%m-%d %H-%M-%S")
            async with aiofiles.open(log_file, 'a') as f:
                await f.write(f"[{timestamp}] File1: {occ1}, File2: {occ2}\n")
            print(f"[{time.strftime('%H:%M:%S')}] Logged counts -> File1: {occ1}, File2: {occ2}")
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        print("Logger task cancelled.")
        raise

async def main():
    file1, file2, console_file = 'file1.txt', 'file2.txt', 'counts.log'

    for fname in [file1, file2, console_file]:
        open(fname, 'w').close()

    # create tasks
    tasks = [
        asyncio.create_task(write_to_file(file1, 1), name="writer1"),
        asyncio.create_task(write_to_file(file2, 2), name="writer2"),
        asyncio.create_task(log_occurrence(console_file, 3), name="logger")
    ]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        for t in tasks:
            if not t.done():
                t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        print("All tasks shut down.")

if __name__ == '__main__':
    start = time.time()
    print("File monitoring system started. Press Ctrl+C to stop.")
    try:
        asyncio.run(main())
    finally: 
        end = time.time()
        print(f"\nShutdown complete. Time: {end - start:.2f}s")