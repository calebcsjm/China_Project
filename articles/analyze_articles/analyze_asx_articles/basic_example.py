import multiprocessing

def worker(num):
    """Simple function to simulate work."""
    result = num * num
    print(f"Worker {num}: Result is {result}")

if __name__ == "__main__":
    # Number of processes to create
    num_processes = multiprocessing.cpu_count()

    # Create a pool of processes
    pool = multiprocessing.Pool(processes=num_processes)

    # Map the worker function to the pool of processes
    # Each process will execute the worker function with a different argument
    pool.map(worker, range(num_processes))

    # Close the pool to prevent any more tasks from being submitted
    pool.close()

    # Wait for all processes to complete
    pool.join()