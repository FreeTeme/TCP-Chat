import socket
from _thread import start_new_thread
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox


class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Чат-клиент")
        self.master.geometry("500x400")

        self.text_area = scrolledtext.ScrolledText(master, state='disabled', wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entry = tk.Entry(master)
        self.entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.entry.bind("<Return>", self.send_message)

        self.username = simpledialog.askstring("Имя", "Введите ваше имя:", parent=master)
        if not self.username:
            messagebox.showerror("Ошибка", "Имя не может быть пустым")
            master.destroy()
            return

        self.client_ip = simpledialog.askstring("IP клиента", "Введите ваш IP:", parent=master) or "127.0.0.2"
        self.server_ip = simpledialog.askstring("IP сервера", "Введите IP сервера:", parent=master) or "127.0.0.1"
        self.client_port = simpledialog.askinteger("Порт клиента", "Введите порт клиента:", parent=master) or 0
        self.server_port = simpledialog.askinteger("Порт сервера", "Введите порт сервера:", parent=master) or 8080

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.sock.bind((self.client_ip, self.client_port))
            self.sock.connect((self.server_ip, self.server_port))
            self.sock.send(self.username.encode("utf-8"))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {e}")
            master.destroy()
            return

        start_new_thread(self.receive, ())

    def append_text(self, msg):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, msg + "\n")
        self.text_area.yview(tk.END)
        self.text_area.config(state='disabled')

    def send_message(self, event=None):
        message = self.entry.get().strip()
        if message:
            try:
                self.sock.send(message.encode("utf-8"))
                self.entry.delete(0, tk.END)
            except Exception as e:
                self.append_text(f"Ошибка отправки: {e}")

    def receive(self):
        while True:
            try:
                data = self.sock.recv(1024).decode("utf-8")
                if not data:
                    self.append_text("🔌 Соединение закрыто сервером.")
                    break
                self.append_text(data)
            except:
                self.append_text("❌ Ошибка соединения.")
                break
        self.sock.close()
        self.master.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
