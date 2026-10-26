import socket
import threading
import tkinter as tk
from queue import Queue

PORT = 5000


class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Pulse Chat")
        self.root.geometry("500x500")
        self.sock = None
        self.connected = False
        self.events = Queue()
        tk.Label(root, text="Username:").pack()
        self.name_entry = tk.Entry(root)
        self.name_entry.pack(fill="x", padx=10)
        self.connect_btn = tk.Button(
            root, text="Connect", command=self.connect
        )
        self.connect_btn.pack(pady=5)
        self.chat_area = tk.Text(root, state="disabled")
        self.chat_area.pack(fill="both", expand=True, padx=10, pady=5)
        self.message_entry = tk.Entry(root, state="disabled")
        self.message_entry.pack(fill="x", padx=10)
        self.message_entry.bind("<Return>", self.send_message)
        self.send_btn = tk.Button(
            root, text="Send",
            command=self.send_message, state="disabled"
        )
        self.send_btn.pack(pady=5)
        self.root.after(100, self.process_messages)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def connect(self):
        username = self.name_entry.get().strip()

        if not username:
            return

        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.sock.connect(("127.0.0.1", PORT))
        self.sock.sendall((username + "\n").encode("utf-8"))

        self.connected = True
        self.name_entry.config(state="disabled")
        self.connect_btn.config(state="disabled")
        self.message_entry.config(state="normal")
        self.send_btn.config(state="normal")

        threading.Thread(
            target=self.receive_messages,
            daemon=True
        ).start()

    def receive_messages(self):
        reader = self.sock.makefile("r", encoding="utf-8")

        for message in reader:
            self.events.put(message.strip())

        reader.close()
        self.events.put(None)

    def send_message(self, event=None):
        if not self.connected:
            return

        message = self.message_entry.get().strip()

        if not message:
            return

        self.sock.sendall((message + "\n").encode("utf-8"))
        self.message_entry.delete(0, "end")

    def process_messages(self):
        while not self.events.empty():
            message = self.events.get()

            if message is None:
                self.connected = False
                self.message_entry.config(state="disabled")
                self.send_btn.config(state="disabled")
                self.name_entry.config(state="normal")
                self.connect_btn.config(state="normal")
                self.display_message("Disconnected from server.")
                break

            self.display_message(message)

        self.root.after(100, self.process_messages)

    def display_message(self, message):
        self.chat_area.config(state="normal")
        self.chat_area.insert("end", message + "\n")
        self.chat_area.see("end")
        self.chat_area.config(state="disabled")

    def close_app(self):
        self.connected = False

        if self.sock:
            self.sock.sendall(b"/quit\n")
            self.sock.close()

        self.root.destroy()

root = tk.Tk()
app = ChatClient(root)
root.mainloop()