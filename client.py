import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")
        self.setup_ui()
        
    def setup_ui(self):
        # Frame для подключения
        conn_frame = ttk.Frame(self.root, padding=10)
        conn_frame.pack(fill=tk.X)
        
        # Настройки сервера
        ttk.Label(conn_frame, text="Server:").grid(row=0, column=0)
        self.server_ip = ttk.Entry(conn_frame, width=15)
        self.server_ip.grid(row=0, column=1, padx=5)
        self.server_ip.insert(0, "127.0.0.1")
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2)
        self.server_port = ttk.Entry(conn_frame, width=8)
        self.server_port.grid(row=0, column=3, padx=5)
        self.server_port.insert(0, "5555")
        
        # Настройки клиента
        ttk.Label(conn_frame, text="Your IP:").grid(row=1, column=0)
        self.client_ip = ttk.Entry(conn_frame, width=15)
        self.client_ip.grid(row=1, column=1, padx=5)
        self.client_ip.insert(0, "127.0.0.2")
        
        ttk.Label(conn_frame, text="Your Port:").grid(row=1, column=2)
        self.client_port = ttk.Entry(conn_frame, width=8)
        self.client_port.grid(row=1, column=3, padx=5)
        self.client_port.insert(0, "60001")
        
        ttk.Label(conn_frame, text="Name:").grid(row=2, column=0)
        self.client_name = ttk.Entry(conn_frame, width=15)
        self.client_name.grid(row=2, column=1, padx=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=2, column=3, columnspan=2)
        
        # Чат
        self.chat_area = scrolledtext.ScrolledText(self.root, width=60, height=20, state='disabled')
        self.chat_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=(0, 5))
        
        # Ввод сообщения
        input_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        input_frame.pack(fill=tk.X)
        
        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_entry.bind("<Return>", self.send_message)
        
        self.send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT)
        
        self.set_ui_state(False)
        
    def set_ui_state(self, connected):
        state = tk.NORMAL if connected else tk.DISABLED
        self.message_entry.config(state=state)
        self.send_btn.config(state=state)
        self.connect_btn.config(text="Disconnect" if connected else "Connect")
        
        for entry in [self.server_ip, self.server_port, self.client_ip, self.client_port, self.client_name]:
            entry.config(state=tk.DISABLED if connected else tk.NORMAL)
            
    def toggle_connection(self):
        if hasattr(self, 'connected') and self.connected:
            self.disconnect()
        else:
            self.connect()
            
    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Привязываемся к указанному клиентскому IP:PORT
            self.sock.bind((self.client_ip.get(), int(self.client_port.get())))
            
            # Подключаемся к серверу
            self.sock.connect((self.server_ip.get(), int(self.server_port.get())))
            
            # Отправляем имя
            name = self.client_name.get().strip()
            if not name:
                raise ValueError("Name cannot be empty")
            self.sock.send(name.encode('utf-8'))
            
            self.connected = True
            self.set_ui_state(True)
            self.log("Connected to server")
            
            # Запускаем поток для приема сообщений
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            if hasattr(self, 'sock'):
                self.sock.close()
                
    def disconnect(self):
        self.connected = False
        try:
            self.sock.close()
        except:
            pass
        self.set_ui_state(False)
        self.log("Disconnected from server")
        
    def receive_messages(self):
        while self.connected:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                self.log(data.decode('utf-8'))
            except:
                if self.connected:
                    self.log("Connection lost")
                break
                
        self.disconnect()
        
    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message and self.connected:
            try:
                full_message = f"{self.client_name.get()}: {message}"
                self.sock.send(message.encode('utf-8'))
                self.log(full_message)  # Добавляем в чат сразу
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                self.log(f"Send error: {e}")
                self.disconnect()

                
    def log(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()