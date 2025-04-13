import socket
import threading
from datetime import datetime

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}  # {socket: (ip, port, name)}
        self.server_socket = None
        self.running = False

    def start(self):
        self.running = True
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Сервер запущен на {self.host}:{self.port}")
            
            while self.running:
                client_socket, (client_ip, client_port) = self.server_socket.accept()
                threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_ip, client_port),
                    daemon=True
                ).start()
                
        except Exception as e:
            print(f"Ошибка сервера: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def handle_client(self, sock, ip, port):
        try:
            # Получаем имя клиента
            name = sock.recv(1024).decode('utf-8').strip()
            with threading.Lock():
                self.clients[sock] = (ip, port, name)
            
            print(f"[{datetime.now().strftime('%H:%M')}] {name} ({ip}:{port}) подключился")
            
            # Основной цикл обработки сообщений
            while self.running:
                data = sock.recv(1024)
                if not data:
                    break
                    
                message = data.decode('utf-8')
                print(f"[{datetime.now().strftime('%H:%M')}] {name}: {message}")
                
                # Рассылка сообщения всем клиентам
                self.broadcast(f"{name}: {message}", exclude_sock=sock)
                
        except Exception as e:
            print(f"Ошибка клиента {ip}:{port}: {e}")
        finally:
            self.cleanup_client(sock)

    def broadcast(self, message, exclude_sock=None):
        with threading.Lock():
            for sock in list(self.clients.keys()):
                if sock != exclude_sock:
                    try:
                        sock.sendall(message.encode('utf-8'))
                    except:
                        self.cleanup_client(sock)

    def cleanup_client(self, sock):
        if sock in self.clients:
            ip, port, name = self.clients[sock]
            print(f"[{datetime.now().strftime('%H:%M')}] {name} ({ip}:{port}) отключился")
            with threading.Lock():
                del self.clients[sock]
            sock.close()

if __name__ == "__main__":
    server_ip = input("Введите IP сервера (например 127.0.0.1): ")
    server_port = int(input("Введите порт сервера (например 5555): "))
    server = ChatServer(server_ip, server_port)
    server.start()