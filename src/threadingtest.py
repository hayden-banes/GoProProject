import threading
import time

def thread_function_1(stop_event):
    while not stop_event.is_set():
        print("Thread 1 is running")
        time.sleep(1)

def thread_function_2(stop_event):
    while not stop_event.is_set():
        print("Thread 2 is running")
        time.sleep(1)

# Create event objects for each thread to signal stop
stop_event_1 = threading.Event()
stop_event_2 = threading.Event()

# Create two new threads
thread_1 = threading.Thread(target=thread_function_1, args=(stop_event_1,))
thread_2 = threading.Thread(target=thread_function_2, args=(stop_event_2,))

# Start the new threads
thread_1.start()
thread_2.start()

# Main thread continues executing
print("Main thread is running")

# Wait for user input to stop threads
input("Press Enter to stop threads...")

# Send signal to stop the threads
stop_event_1.set()
stop_event_2.set()

# Wait for the threads to finish
thread_1.join()
thread_2.join()

print("Main thread ended")