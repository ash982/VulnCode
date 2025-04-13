import pickle
import socket

def serialize_data(data, ip, port):
    # Serialize the data
    serialized_data = pickle.dumps(data)
    
    # Send the serialized data to the IP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(serialized_data)
    
    print(f"Data serialized and sent to {ip}:{port}")

def deserialize_data(ip, port):
    # Receive the serialized data from the IP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            received_data = conn.recv(1024) 
    
    # Deserialize the data
    deserialized_data = pickle.loads(received_data) # deserialize data from web socket
    
    print(f"Data received and deserialized from {addr}")
    return deserialized_data

# Example usage
if __name__ == "__main__":
    data_to_send = {"key": "value", "list": [1, 2, 3]}
    ip = "127.0.0.1"  # this can be replaced with external untrusted IP
    port = 65432

    serialize_data(data_to_send, ip, port)
    received_data = deserialize_data(ip, port)
    print("Received data:", received_data)

