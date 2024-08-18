import socket
import threading
import csv

clients = {}
client_names = {}

# Fonction pour gérer chaque client
def handle_client(client_socket, addr):
    with client_socket:
        pseudo = client_socket.recv(1024).decode()
        client_id = addr[1]
        clients[client_socket] = pseudo
        client_names[client_socket] = client_id
        print(f"{pseudo} has connected from {addr}")
        
        # Envoyer l'historique des messages au nouveau client
        send_message_history(client_socket)
        
        while True:
            try:
                msg = client_socket.recv(1024).decode()
                if not msg:
                    break
                broadcast(f"{pseudo}: {msg}", client_socket)
                save_message(pseudo, msg)
            except:
                clients.pop(client_socket)
                break

# Fonction pour envoyer un message à tous les clients
def broadcast(message, sender_socket):
    for client in clients:
        try:
            client.sendall((message + "\n").encode())  # Ajouter une nouvelle ligne après chaque message
        except:
            client.close()
            clients.pop(client)

# Fonction pour enregistrer les messages dans un fichier CSV
def save_message(pseudo, message):
    with open('chat_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([pseudo, message])

# Fonction pour envoyer l'historique des messages à un client
def send_message_history(client_socket):
    try:
        with open('chat_log.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                message = f"{row[0]}: {row[1]}"
                client_socket.sendall((message + "\n").encode())  # Ajouter une nouvelle ligne après chaque message
    except FileNotFoundError:
        pass  # Si le fichier n'existe pas encore, on ne fait rien

# Initialiser et lancer le serveur
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('192.168.105.31', 4321))
    server.listen()
    print("Server started and listening on port 4321")

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

start_server()
