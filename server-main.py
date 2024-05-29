import socket
import requests


def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException:
        return None


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # On utilise une adresse arbitraire pour forcer la découverte de l'IP locale
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None


def main():
    # Configuration du serveur
    HOST = '0.0.0.0'  # Adresse IP du serveur
    PORT = 12345      # Port d'écoute du serveur

    # Tentative de récupération de l'adresse IP publique
    public_ip = get_public_ip()
    if public_ip:
        print(f"Adresse IP publique: {public_ip}")

    else:
        print("Impossible de récupérer l'adresse IP publique.")

    # Récupération de l'adresse IP locale
    local_ip = get_local_ip()
    if local_ip:
        print(f"Adresse IP locale: {local_ip}")
        HOST = local_ip
    else:
        print("Impossible de récupérer l'adresse IP locale.")

    # Création du socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Serveur en écoute sur {HOST}:{PORT}")

    conn, addr = server_socket.accept()
    print(f"Connexion acceptée de {addr}")

    # Écho des messages reçus
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Reçu du client: {data.decode()}")
            conn.sendall(data)
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        conn.close()
        server_socket.close()


if __name__ == "__main__":
    main()
    print('Hello World')

