from threading import Thread
import server
import client
import time


def main():
    server1 = server.Server(('localhost', 8080), server.configTCPHandler())
    serverThread = Thread(target=server1.serve_forever)
    serverThread.start()
    print(f"Server running")
    time.sleep(1)
    client1 = client.Client('Test1')
    client1.send_math_expressions()
    #Thread(target=client1.receive_msg).start()
    #client.Client('Test2')
    #client.Client('Test3')
    time.sleep(2)
    print(f"Program exit")
    exit()


if __name__ == "__main__":
    main()