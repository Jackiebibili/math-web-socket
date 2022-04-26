from threading import Thread
import server
import client
import time


def main():
    server1 = server.Server(('localhost', 8080), server.TCPHandler)
    serverThread = Thread(target=server1.serve_forever)
    serverThread.start()
    time.sleep(1)
    client1 = client.Client('Test1')
    client2 = client.Client('Test2')
    client3 = client.Client('Test3')
    time.sleep(2)
    exit()


if __name__ == "__main__":
    main()