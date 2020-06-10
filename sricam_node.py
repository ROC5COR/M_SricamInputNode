from SricamInputNode import SricamInputNode
import threading

print("SricamInputNode")
input_node = SricamInputNode("rtsp://192.168.0.27/onvif1", 8000)

video_thread = threading.Thread(target=input_node.start_video_capture)
video_thread.start()

server_thread = threading.Thread(target=input_node.start_server)
server_thread.start()

video_thread.join()
server_thread.join()


