import falcon
from wsgiref import simple_server
import json
import cv2
import os
import threading

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0" # Setting this otherwise fail to load rtsp feed
NODE_IDENTITY = "SricamInputNode"


class SricamInputNode(threading.Thread):
    def __init__(self, listening_port):
        threading.Thread.__init__(self)
        stream_address = os.environ.get('SricamInputNode_StreamAddress', None)
        if stream_address is None:
            print("Missing SricamInputNode_StreamAddress in envs")
            return
            
        self.capture_device = cv2.VideoCapture(stream_address)
        self.latest_frame = None

        class MainRoute:
            def on_get(self, req, res):
                res.body = NODE_IDENTITY

        class FrameRoute:
            def __init__(self, parent_refenrence):
                self.parent = parent_refenrence

            def on_get(self, req, res):
                _, encoded_frame = cv2.imencode('.jpg', self.parent.get_latest_frame())
                #res.media = {'data',encoded_frame.tobytes()} # Numpy function
                res.content_type = 'image/jpeg'
                res.data = encoded_frame.tobytes() # Numpy function
                #res.stream = encoded_frame.tobytes()
                #res.stream_len = len(encoded_frame)


        api = falcon.API()
        api.add_route('/', MainRoute())
        api.add_route('/frame', FrameRoute(self))
        self.server = simple_server.make_server('', listening_port, app=api)

    def get_latest_frame(self):
        return self.latest_frame

    def start_video_capture(self):
        #i = 0
        print("[INFO] Starting video")
        while True:
            if self.capture_device.isOpened():
                ret, frame = self.capture_device.read()
                if not ret:
                    print("[ERROR] Error while fetching frame")
                    self.frame = None
                    continue
                self.latest_frame = frame

    def start_server(self):
        print("[INFO] Starting server")
        self.server.serve_forever()

    def run(self):
        video_thread = threading.Thread(target=self.start_video_capture)
        video_thread.start()

        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()

        video_thread.join()
        server_thread.join()
