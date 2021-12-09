import socket 
import threading
import string

HEADER: int = 64
PORT: int = 5003
# SERVER: str = '0.0.0.0'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT: str = 'utf-8'
DISCONNECT_MESSAGE: str = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

rooms = {}
print('Socket successfully created')

server.bind(ADDR)
print(f'socket binded to {ADDR}')

clients = []

class Client:
    connection: socket
    address: tuple
    room_name: string
    user_name: string
    
def msg_handler(conn: socket, addr: tuple):
    # Register for a room
    conn.send('Please provide a room name:'.encode(FORMAT))
    msg_length = int(conn.recv(HEADER).decode(FORMAT))
    room_name = conn.recv(msg_length).decode(FORMAT)
    target_client: Client
    for client in clients:
        if client.connection is conn:
            client.room_name = room_name
            target_client = client
    conn.send('Room registered'.encode(FORMAT))
    print(rooms[room_name])
    # Recieve and transmit messagees
    try:
        connected = True
        while connected:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT_MESSAGE:
                    connected = False
                    break
                print(f"[{addr}] {msg}")
                # Filter out of room broadcast
                for client in clients:
                    if client.room_name == room_name:
                        if client is not target_client:
                            client.connection.send(f"[{addr}] {msg}".encode(FORMAT))
                        else:
                            conn.send("Msg received".encode(FORMAT))

        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
        conn.close()
    except Exception as ex:
        print(str(ex))
    
def client_handler():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, client_address = server.accept()
        conn.send('You are connected'.encode(FORMAT))
        client: Client = Client()
        client.connection = conn
        client.address = client_address
        clients.append(client)
        thread = threading.Thread(target=msg_handler, args=(conn, client_address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

print("[STARTING] server is starting...")
client_handler()