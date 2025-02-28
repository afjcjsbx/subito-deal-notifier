import asyncio

class AsyncProcessor:
    """Manages an asynchronous queue for sequentially processing heavy tasks."""

    def __init__(self):
        self.queue = asyncio.Queue()

    async def process_queue(self):
        """Continuously processes tasks from the queue asynchronously."""
        print("🚀 Task processor started")
        while True:
            func, args = await self.queue.get()  # Wait for the next task
            try:
                print(f"⚡ Executing {func.__name__} with args {args}")
                await func(*args)  # ⬅️ Usa await invece di asyncio.create_task
            except Exception as e:
                print(f"❌ Error processing task {args}: {e}")
            self.queue.task_done()  # Mark task as completed

    async def add_task(self, func, *args):
        """Adds a new task to the queue."""
        await self.queue.put((func, args))
        print(f"📌 New async task added: {func.__name__} with args {args}")

