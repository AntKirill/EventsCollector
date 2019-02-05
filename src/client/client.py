import socket
import sys

sys.path.append('../')
import src.server_api as server_api

# TODO: read this from config

HOST, PORT = "localhost", 9999


def main():
    send_request(sys.argv[1:])


def send_request(request):
    data = " ".join(request)
    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        server_api.parse_arguments(request)
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(bytes(data + "\n", "utf-8"))


if __name__ == '__main__':
    main()
