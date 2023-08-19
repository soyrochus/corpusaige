import tkinter as tk
from tkinter import ttk
import threading

def exec_task_with_progress(root, title, task):
    def task_wrapper():
        task()
        popup.quit()

    # Create the popup
    popup = tk.Toplevel()
    popup.title(title)
    #popup.title('Processing...')
    
    # Make the popup always stay on top of other windows
    popup.attributes('-topmost', True)

    # Keep the focus on the popup until task completion
    popup.grab_set()

    # Create and pack the progress bar
    progress = ttk.Progressbar(popup, orient="horizontal", mode="indeterminate")
    progress.pack(pady=20, padx=20)
    progress.start()

    # Update idle tasks to compute window sizes
    popup.update_idletasks()

    # Set a width for the popup window (for example, 300 pixels)
    desired_width = 300
    x = root.winfo_x() + (root.winfo_width() / 2) - (desired_width / 2)
    y = root.winfo_y() + (root.winfo_height() / 2) - (popup.winfo_height() / 2)

    # Adjust the geometry of the popup window
    popup.geometry(f"{desired_width}x{popup.winfo_height()}+{int(x)}+{int(y)}")

    # Start the long-running task in a background thread
    task_thread = threading.Thread(target=task_wrapper)
    task_thread.start()

    # This will run the tkinter main loop until task_thread completes and calls popup.quit()
    popup.mainloop()

    # Cleanup after task finishes
    progress.stop()
    task_thread.join()
    popup.destroy()


# def long_running_task():
#     time.sleep(10)  # Simulate a long-running task

# # This is an example of integrating with an existing tkinter application:
# root = tk.Tk()
# root.title("Main Application")

# def create_task(root, task):
#     def _task_handler():
#         exec_task_with_progress(root, task)
#     return _task_handler