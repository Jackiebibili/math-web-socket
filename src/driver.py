from threading import Thread
import server, client, time, random, os

def main():
    ## configure and start the server
    TCPHandler, message_forwarder = server.configTCPHandler()
    server1 = server.Server(('localhost', 8080), TCPHandler)
    serverThread1 = Thread(target=server1.serve_forever)
    serverThread1.setDaemon(True)
    serverThread1.start()
    serverThread2 = Thread(target=message_forwarder)
    serverThread2.setDaemon(True)
    serverThread2.start()
    print(f"server running is running at port {server.PORT}")

    # prepare math expressions
    # nested array
    # for client i, its expressions are in math_expr_list[i]
    numberOfclient = 4 # initialize the total number of clients
    numberOfExprs = 3
    math_expr_list = prepare_math_expressions(
        numberOfExprs, numberOfclient, 0)

    ## start clients
    clientList = [] # list of client objects
    threadList = [] # list of client thread
    indexCount = 0
    for clientNum in range(numberOfclient): # create client based of numberOfClient
        clientList.append(client.Client('Client %d'%clientNum))
    for clientP in clientList:
        threadList.append(Thread(target=clientP.receive_msg))
        threadList[indexCount].setDaemon(True)
        threadList[indexCount].start()
        Thread(target=lambda: clientP.send_math_expressions(
            math_expr_list[indexCount])).start()
        indexCount += 1

    time.sleep(3)
    write_log_to_file()
    print(f"program finishes - server is closing")
    os._exit(0)
    

def generate_single_random_expr():
    return '(%d%s%d)' % (random.randint(1, 10), generate_operator(), random.randint(1, 10))
def generate_random_expr(depth):
    if depth == 0:
        return generate_single_random_expr()
    return '(%s%s%s)' % (generate_random_expr(depth - 1), generate_operator(), generate_random_expr(depth - 1))

OPERATOR_MAP = {
    1: '+',
    2: '-',
    3: '*',
}
def generate_operator():
    return OPERATOR_MAP[random.randint(1,3)]

def prepare_math_expressions(num_exprs, num_groups, depth):
    res = []
    for i in range(num_groups):
        res.append([])
        for _ in range(num_exprs):
            res[i].append(generate_random_expr(depth))
    return res

def write_log_to_file():
    out = open("output.txt", "w")
    while not server.log_queue.empty():
        log_line = server.log_queue.get()
        out.write(log_line)
    out.close()


if __name__ == "__main__":
    main()
