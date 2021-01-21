from flask import Flask
from flask import Response
from flask import render_template
from imutils.video import VideoStream
import threading
import time
import cv2


output_frame = None
lock = threading.Lock()

app = Flask(__name__)

vs = VideoStream(src=0).start()
time.sleep(2.0)


def streamer():
    global vs, output_frame, lock
    while True:
        frame = vs.read()
        with lock:
            output_frame = frame.copy()


def generate():
    # grab global references to the output frame and lock variables
    global output_frame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if output_frame is None:
                print(output_frame)
                continue
            # encode the frame in JPEG format
            (flag, encoded_image) = cv2.imencode(".jpg", output_frame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encoded_image) + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed/')
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    t = threading.Thread(target=streamer)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=8000, debug=True,
            threaded=True, use_reloader=False)

vs.stop()
