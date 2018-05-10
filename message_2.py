import threading
import time
import socket
import struct
import sys
import json
import select
from main import main
from packet_route import route

main = main()
router= route()
RECV_BUFFER=1024
zero = 0
protocol = 17
def recieve_msg(_socket,listen,peer_port,peer_ip,cost,node_id):
    _socket.bind(('', listen))
    host = socket.gethostbyname(socket.gethostname())
    router.self_id = str(host) + ":" + str(listen)
    #set neighbour IP and initialize routing table
    n_ip = socket.gethostbyname(peer_ip)
    neighbor_id = str(n_ip) + ":" + peer_port
    #Fill routing data
    router.routing_table[neighbor_id] = {}
    router.routing_table[neighbor_id]['cost'] = cost
    router.routing_table[neighbor_id]['link'] = neighbor_id
    router.routing_table[neighbor_id]['email'] = node_id
    router.adjacent_links[neighbor_id] = cost
    router.neighbors[neighbor_id] = {}
    router.time_out=main.time_out()
    router.email=node_id

    print ("bfclient running at address [%s] on port [%s]" % (str(host), listen))
    # router.update_timer(_socket,route.time_out)
    # router.node_timer(_socket,route.time_out)
    option =main.menu()
    if option==1:
        router.msg_prompt()
    elif option == 2:
        router.msg_prompt()
    elif option == 3:
        pass
    else:
        router.msg_prompt()
    while True:
        socket_list = [sys.stdin,_socket]
        try:
            read_sockets, write_sockets, error_sockets = select.select(socket_list,[],[])
        except select.error:
            break
        except socket.error:
            break
        for sock in read_sockets:
            if sock == _socket:
                data, addr = _socket.recvfrom(RECV_BUFFER)
                if data:
                    msg = json.loads(data.decode('utf-8'))
                    router.msg_handler(serverSocket,msg, addr)
                    time.sleep(0.1)
                else:
                    print ("[Error] 0 bytes received.")
            else:
                data = sys.stdin.readline().rstrip()
                if len(data) > 0:
                    data_list = data.split()
                    router.cmd_handler(serverSocket,data_list)
                    router.prompt()
                else:
                    sys.stdout.flush()
                    router.prompt()
    _socket.close()

def private_msg(data):
    packet = router.parse(data)
    ip_addr = struct.pack('!8B', *[data[x] for x in range(12, 12 + 8)])
    udp_psuedo = struct.pack('!BB5H', zero, protocol, packet['udp_length'], packet['src_port'], packet['dest_port'], packet['udp_length'], 0)
    verify = router.verify_checksum(ip_addr + udp_psuedo + bytes(packet['data'].encode('utf-8')), packet['UDP_checksum'])
    if verify == 0xFFFF:
        print( packet['data'])
        time.sleep(0.1)
    else:
        print('Checksum Error!Packet is discarded')


if __name__ == '__main__':
    peer_ip = main.login()
    peer_port=main.peer_port()
    src_port = main.src_port()
    dest_port = main.dest_port()
    node_id= main.node_id()
    cost = main.cost_matrix()
    time_out= main.time_out()
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    recieve_msg(serverSocket,src_port,peer_port,peer_ip,cost,node_id)
   


