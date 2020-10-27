
# recieve length of file
import socket, sys, time, hashlib, multiprocessing

# PORT0 = 12345
# HOST = '192.168.178.2'
HOST = ''
def receive(conn, timeout, length):
    try:
        if timeout is not None:
            conn.settimeout(timeout)
        message = conn.recv(length)
    except socket.timeout:
        return -1
    return message

def start(PORT0):
    # init socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT0))
    sock.listen()

    try:
        # connect socket
        conn, _ = sock.accept()
    except:
        e = sys.exc_info()[0]
        print( "catched <p>Error: %s</p>" % e )
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
        return -1

    # recieve file length
    length = int(receive(conn, None, 2048))
    print(length)

    # signal readyness
    conn.sendall('ready'.encode('utf8'))

    # recieve hash of file
    file_hash = receive(conn, None, 2048).decode('utf8')
    
    # signal readyness
    conn.sendall('ready'.encode('utf8'))
    
    # recieve file and calculate duration
    rec_file = []
    i = 0
    start_time = time.time()
    while i < length:
        j = receive(conn, 1, (min(length - i, 4096)))
        if j == -1:
            break
        rec_file.append(j)
        i += len(j)
    duration = time.time() - start_time
    rec_file = b''.join(rec_file)
    print('duration: ', duration)
    
    # calculate checksum
    md5_hash = hashlib.md5()
    md5_hash.update(rec_file)
    file_hash2 = md5_hash.hexdigest()
    print('file_hash: ', file_hash)
    print('file_hash neu', file_hash2)
    # send duration time if checksum checs out, else -1 
    if file_hash == file_hash2:
        ans = str(duration).encode('utf8')
    else:
        ans = str(-1).encode('utf8')
    conn.sendall(ans)
    print('closed')
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
    return


def run():
    processes = []
    for i in range(11110, 11140):
        process = multiprocessing.Process(target=start, args=(i,))
        process.start()
        processes.append(process)
    for j in processes:
        j.join()
    return

def run_single():
    start(11141)
