import asyncio
import time

async def fetch_data(param):
    await asyncio.sleep(param)
    return f"Result of {param}"

async def main():
    # 1. Create Tasks Manually
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    result1 = await task1
    result2 = await task2
    print(f"Task 1 and 2 awaited results: {[result1, result2]}")

    # 2. Gather Coroutines
    # Passes raw coroutine objects. gather wraps them in tasks under the hood.
    coroutines = [fetch_data(i) for i in range(1, 3)]
    results = await asyncio.gather(*coroutines, return_exceptions=True)
    print(f"Coroutine Results: {results}")

    # 3. Gather Tasks
    # Passes already-created Task objects.
    tasks = [asyncio.create_task(fetch_data(i)) for i in range(1, 3)]
    results = await asyncio.gather(*tasks)
    print(f"Task Results: {results}")

    # 4. Task Group (Python 3.11+)
    async with asyncio.TaskGroup() as tg:
        results = [tg.create_task(fetch_data(i)) for i in range(1, 3)]
        # All tasks are awaited implicitly when the context manager exits.
    print(f"Task Group Results: {[result.result() for result in results]}")

    return "Main Coroutine Done"

t1 = time.perf_counter()
results = asyncio.run(main())
print(results)
t2 = time.perf_counter()
print(f"Finished in {t2 - t1:.2f} seconds")

'''
Execution Flow (The Animation)
Manual Block: Schedules task 1 and task 2. Awaits task 1 (takes 1s), then awaits task 2 (takes 2s). Total: ~3s.
Gather Coroutines Block: Creates a list of 2 coroutine objects. asyncio.gather takes them, schedules them concurrently, and pauses main(). Once both finish (~2s), it returns the list of results. If one had failed, the exception object would literally be in the list because of return_exceptions=True.
Gather Tasks Block: Exactly the same as block 2, except we explicitly wrapped them in create_task before passing them to gather.
TaskGroup Block: We enter the async with block. We create 2 tasks. As soon as the code hits the end of the with block, the TaskGroup says "Wait! Don't leave yet." It implicitly awaits both tasks. If task 2 had crashed here, TaskGroup would have instantly cancelled task 1, gathered the exceptions, and thrown an ExceptionGroup error, stopping the program. Since they succeed, it extracts the results using result.result().
Total Time: ~9.00 seconds (3s + 2s + 2s + 2s, as each block runs sequentially after the previous one).
'''
