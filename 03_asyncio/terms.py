import asyncio
import time

# SYNC FUNCTION — blocks the thread. Cannot be awaited directly.
def sync_function(test_param: str) -> str:
    print("This is a synchronous function.")
    time.sleep(0.1)  # ❌ blocks the event loop if called inside async code
    return f"Sync Result: {test_param}"

# COROUTINE FUNCTION — calling this returns a coroutine object, doesn't run yet.
async def async_function(test_param: str) -> str:
    print("This is an asynchronous coroutine function.")
    await asyncio.sleep(0.1)  # ✅ non-blocking; yields control to event loop
    return f"Async Result: {test_param}"

async def main():
    # --- Future demo ---
    # loop = asyncio.get_running_loop()
    # future = loop.create_future()           # pending Future
    # future.set_result("Future Result: Test")
    # future_result = await future            # retrieves the value
    
    # --- Coroutine object demo ---
    # coroutine_obj = async_function("Test")  # creates CORO_CREATED object
    # coroutine_result = await coroutine_obj   # executes it sequentially
    
    # --- Task demo (concurrent execution) ---
    task = asyncio.create_task(async_function("Test"))  # schedules on event loop
    print(task)             # <Task pending ...>
    task_result = await task  # waits for completion, gets result
    print(task_result)       # "Async Result: Test"

if __name__ == "__main__":
    asyncio.run(main())  # creates loop → runs main() → closes loop