# Asyncio Notes

### What is Asyncio?

Asyncio is a Python library used to write concurrent code using a single thread and a single process. It is designed primarily for I/O-bound tasks. It uses what is called cooperative multitasking, where tasks voluntarily yield control back to the event loop at await points (unlike preemptive multitasking where the OS forces context switches).

#### Key interview points:

- It provides concurrency, not parallelism. True parallelism requires multiprocessing.
- Best suited for I/O-bound tasks (network calls, file I/O, DB queries) — not CPU-bound tasks.
- Reduces overhead of thread context-switching and avoids GIL issues that threads face (though asyncio runs under the GIL, it doesn't need multiple threads).

---

### Concurrency vs Parallelism (frequently asked)

| | Concurrency | Parallelism |
|---|---|---|
| Definition | Multiple tasks making progress (interleaved) | Multiple tasks running at the same instant |
| Asyncio | ✅ | ❌ |
| Threading | ✅ (limited by GIL) | ❌ (in CPython) |
| Multiprocessing | ✅ | ✅ |

---

### Event Loop

The Event Loop is the central orchestrator of asyncio. Think of it as the engine that runs and manages asynchronous functions. It keeps track of all pending tasks, and when a task is waiting for I/O (and yields control), the loop pauses it and picks up another ready task to work on. `asyncio.run()` is responsible for getting this event loop, running our main task until it completes, and then safely shutting down the loop.

#### Execution Flow & Priority (How it works internally):

- The event loop maintains a queue of ready-to-run callbacks and coroutines.
- It doesn't strictly use "priorities" (like 1, 2, 3). Instead, it generally processes tasks in a FIFO (First-In, First-Out) manner.
- When a coroutine hits an `await` on something that isn't ready yet, it yields control. The loop takes that coroutine out of the active queue and puts it in a "waiting" state.
- The loop then instantly pulls the next ready coroutine from the queue and starts executing it.
- When the I/O operation finishes, the loop moves the waiting coroutine back to the ready queue to resume exactly where it left off.

---

### What happens if we run Synchronous Code in the Event Loop?

If you run blocking synchronous code (like `time.sleep(5)` or `requests.get())` inside the event loop, the entire event loop freezes.

Because asyncio is single-threaded, the loop cannot pause the sync code or switch to another task. It is trapped.

**Result:** All other coroutines are blocked for the duration of the sync call. The concurrency advantage is completely lost.

---

### About asyncio.run()

`asyncio.run()` is the standard entry point for asyncio programs. It acts as the bridge between the synchronous world and the asynchronous event loop.

When you call `asyncio.run(main())`, it does three critical things:

1. Creates a new event loop.
2. Schedules and runs the provided coroutine (usually `main()`) until it completes.
3. Shuts down async generators and closes the event loop to free up resources.

**Rule of thumb:** It should be called only once per program, typically in the `if **__name__** == "**__main__**":` block. Calling it multiple times in the same thread can lead to errors because it creates and destroys a new loop each time.

---

### Basic Terminology

#### The await keyword

The `await` keyword is used with awaitable objects (objects that implement a special `**__await__**` method under the hood).

When we use `await`, we are telling the event loop to pause the execution of the current function and yield control back to the event loop. The coroutine stays suspended until the awaited task completes.

`await` can only be used inside an `async def` function.

When you await something that's not yet done, the current coroutine suspends, and the event loop is free to run something else. When the awaitable completes, the loop resumes the coroutine from where it paused.

**Interview trick:** If you await something that's already done, it returns immediately without yielding control.

#### Three types of awaitables:

- **Coroutines** — created when you call an `async def` function.
- **Tasks** — coroutines wrapped and scheduled on the event loop.
- **Futures** — low-level objects representing eventual results.

---

### Futures

Futures are more like promises in JavaScript — a container for a result that will be available later. In Python, we rarely work directly with futures. We write coroutines, schedule them as tasks, and then asyncio uses futures under the hood to track those results.

A Future's only job is to hold a certain state and result. The states are: `PENDING → FINISHED` (which could be result-set, exception-set, or cancelled).

**When might you use one?** Usually only when writing low-level async libraries or bridging callback-based code to async/await style. In standard application code, you are never going to use this directly.

### Why await doesn't work with synchronous code

Because synchronous code has no mechanism to work with the event loop. They don't know how to yield control over and resume later.

A regular sync function blocks the entire thread. Since asyncio runs on a single thread, this means the entire event loop freezes.

**Solutions:** Use async equivalents (`asyncio.sleep`, `aiohttp`), or if no async alternative exists, run sync code in a thread/process pool via `asyncio.to_thread()` or `loop.run_in_executor()`.

---

### The Concurrency Trap (Crucial Point)

If you just do `await coroutine_obj` directly, the event loop schedules it and runs it at that exact moment, waiting until it finishes before moving to the next line.

This means it runs sequentially (like normal synchronous code).

You get zero concurrency benefit this way.

To get concurrency, you must wrap it in a Task (`asyncio.create_task(coroutine_obj)`) so the event loop can run it in the background while your main code continues doing other things.

**Warning:** If you create a coroutine and forget to await/schedule it, you get a `RuntimeWarning: coroutine 'x' was never awaited`. The code inside it will never run.

---

### Tasks

Tasks are wrapped around coroutines that can execute independently. Tasks are how we run coroutines concurrently.

When we wrap a coroutine in a task using `asyncio.create_task`, it's handed over to the event loop and scheduled to run whenever it gets a chance. The task keeps track of whether the coroutine finished successfully, raised an exception, or was cancelled — just like futures (under the hood it uses futures), but with extra logic to actually drive the coroutine.

Unlike a raw coroutine, a task can be scheduled on the event loop and just sit there without being actively run until the loop gets control (meaning it runs concurrently in the background). This is the key to asyncio.

### Concurrent execution example:

# Sequential (slow):

r1 = await fetch("url1")   # waits 1s

r2 = await fetch("url2")   # waits 1s  → total 2s

# Concurrent (fast):

t1 = asyncio.create_task(fetch("url1"))

t2 = asyncio.create_task(fetch("url2"))

r1, r2 = await asyncio.gather(t1, t2)   # total ~1s

### Task vs Future

| Aspect | Future | Task |
|---|---|---|
| Wraps | nothing (just a value slot) | a coroutine |
| Created by | `loop.create_future()` | `asyncio.create_task(coro)` |
| Runs code? | No — passive container | Yes — drives the coroutine |
| Used directly? | Rarely | Frequently |

---

### Running Sync Code in Async Context

When there's a place where we don't have any option to work with asyncio and the alternative is sync code to run in async, then we use threads and pools to run the sync code concurrently.

`asyncio.to_thread(func, *args, **kwargs)` (Python 3.9+) — runs a sync function in a separate thread, returns a coroutine you can await. Uses the default `ThreadPoolExecutor`.

`loop.run_in_executor(executor, func, *args)` — more general; works with custom executors (thread or process pools).

For CPU-bound sync work, use `ProcessPoolExecutor` to actually parallelize across cores (escapes the GIL).

For I/O-bound sync work (e.g., requests library), `ThreadPoolExecutor` is fine.



### what points to be rememeber when we covert sync code to async code:
When converting synchronous code to asynchronous code, the very first step is to identify the nature of the workload: Is it I/O-Bound or CPU-Bound?

Step 1: Identify the Workload
    I/O-Bound: Code that spends most of its time waiting for input/output operations to complete (e.g., network requests, database queries, reading/writing files).
    CPU-Bound: Code that spends most of its time actively using the CPU to do heavy math or data processing (e.g., image processing, machine learning, heavy loops, parsing massive JSON).

Step 2: Conversion Rules based on Workload
    If it's I/O-Bound (The ideal scenario for Asyncio):

    Do not use time.sleep(): Replace it with asyncio.sleep().
    Replace blocking libraries: Swap synchronous libraries with their async equivalents.
        Sync: requests ➡️ Async: aiohttp or httpx
        Sync: psycopg2 ➡️ Async: asyncpg or psycopg3
    Add keywords: Add async def to the function definition and await before calling the async library methods.

    If it's CPU-Bound (Do NOT use pure Asyncio):
        If you try to run heavy CPU code inside an async def function, it will block the event loop.
        The Fix: Keep the heavy function synchronous (regular def), and use asyncio.to_thread() or loop.run_in_executor(ProcessPoolExecutor, ...) to run it in the background.

Step 3: The Golden Rule of Async Conversion
    "Async all the way down."
    If you make a function async, everything that calls it must also be async. You cannot call an async def function from a regular def function without using asyncio.run() or an event loop. Once you start converting, it typically cascades through your whole codebase.
 
#### Q: When should we use Asyncio vs Threads vs Processes?
This is the most common concurrency interview question. The answer depends entirely on whether your task is I/O-bound or CPU-bound, and whether you need true parallelism.

1. Asyncio (Coroutines)
    What it is: Single thread, single process, cooperative multitasking.
    When to use: I/O-Bound tasks only.
    Examples: Making 10,000 API requests, querying a database 50 times, waiting for user input.
    Pros: Extremely lightweight (low memory usage), can handle tens of thousands of connections simultaneously, no race conditions (because it's single-threaded).
    Cons: Cannot do CPU-heavy math (blocks the loop), requires async libraries.
2. Threading (threading module)
    What it is: Multiple threads within a single process. In CPython, they are limited by the Global Interpreter Lock (GIL), meaning only one thread runs Python code at a time.
    When to use: I/O-Bound tasks where async libraries don't exist.
    Examples: Scraping a website using the synchronous requests library, or interacting with a legacy C-extension that releases the GIL.
    Pros: Easy to integrate with existing synchronous code.
    Cons: Higher memory overhead than asyncio, GIL prevents true parallelism for Python code, requires locks/mutexes to prevent race conditions on shared data.

3. Multiprocessing (multiprocessing module)
    What it is: Multiple independent processes, each with its own Python interpreter, memory space, and GIL. Achieves true parallelism across multiple CPU cores.
    When to use: CPU-Bound tasks.
    Examples: Image resizing, crunching large CSV files, training ML models, heavy mathematical simulations.
    Pros: True parallelism, bypasses the GIL, fully utilizes multi-core CPUs.
    Cons: Very heavy memory overhead (spawning a process is expensive), inter-process communication (IPC) is slow and complex (data must be pickled/unpickled).


##### Reference for Understanding Through Animation

https://coreyms.com/asyncio/example_1.html
https://coreyms.com/asyncio/example_2.html
https://coreyms.com/asyncio/example_3.html
https://coreyms.com/asyncio/example_4.html
https://coreyms.com/asyncio/example_5.html
https://coreyms.com/asyncio/example_6.html
https://coreyms.com/asyncio/example_7.html




