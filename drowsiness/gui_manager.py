import tkinter as tk
from tkinter import ttk
import constant


class manager:
    def __init__(self):
        pass

    def start_window(self, manager):
        root = tk.Tk()
        root.geometry("400x250")
        root.title("drowsy-detection-program")

        text_frame = ttk.Frame(root, width=50, height=200)
        text_frame.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

        validation_frame = ttk.Frame(root, width=30, height=200)
        validation_frame.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

        button_frame = ttk.Frame(root, width=50, height=200)
        button_frame.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
        mg = tk.StringVar()
        mg.set("CUDA")
        mg1 = tk.StringVar()
        mg1.set("OPENVINO")

        gui_texts = [mg, mg1]

        for i in range(2):
            text = gui_texts[i]
            entry = ttk.Entry(text_frame, state="readonly", textvariable=text, width=1)
            entry.pack(expand=True, fill=tk.X, padx=3, pady=10, side=tk.TOP, ipadx=1)

        test1 = tk.StringVar()
        test2 = tk.StringVar()
        if manager.device == constant.CUDA:
            test1.set("TRUE")
            test2.set("FALSE")
        else:
            test1.set("FALSE")
            test2.set("TRUE")
        gui_texts1 = [test1, test2]

        for i in range(2):
            text = gui_texts1[i]
            entry = ttk.Entry(validation_frame, state="readonly", textvariable=text, width=1)
            entry.pack(expand=True, fill=tk.X, padx=1, pady=10, side=tk.TOP, ipadx=1)

        start_button = ttk.Button(button_frame, text="run", command=manager.start_processes)
        start_button.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, side=tk.TOP)

        def exit_button():
            root.destroy()
            manager.stop_processes()

        stop_button = ttk.Button(button_frame, text="exit", command=exit_button)
        stop_button.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, side=tk.TOP)

        root.protocol("WM_DELETE_WINDOW", manager.stop_processes)
        root.mainloop()

