import time
import zmq
import torch

from laplace_server.server_lhc import ServerLHC
from laplace_server.protocol import (
    DEVICE_CAMERA,
    make_get_request
)

from target_function import target_function

CAMERA_ADDRESS = "tcp://*:5556"
MOTOR_ADDRESS  = "tcp://147.250.140.65:5555"


class DummyCamera:
    def __init__(self, motor_address):
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.REQ)
        self.socket.connect(motor_address)

    def read_motor_position(self):
        self.socket.send_json(
            make_get_request(sender="camera", target="dummy_motor")
        )
        reply = self.socket.recv_json()
        return reply["payload"]["data"]["positions"]

    def measure(self):
        x1, x2 = self.read_motor_position()
        x1 = torch.tensor(x1)
        x2 = torch.tensor(x2)
        result = target_function(x1, x2)
        charge = result[:, 0]
        energy = result[:, 1]

        payload = {
            "electron_charge": charge.tolist(),
            "electron_energy_mean": energy.tolist(),
        }

        print(f"[Camera] Measured {payload}")

        return payload


if __name__ == "__main__":

    camera = DummyCamera(MOTOR_ADDRESS)

    server = ServerLHC(
        address=CAMERA_ADDRESS,
        freedom=2,
        device=DEVICE_CAMERA,
        data={},
        name="dummy_camera"
    )
    print(server.address_for_client)

    def on_get():
        payload = camera.measure()
        # print(f"[Camera] Measured {payload}")
        server.set_data(payload)

    server.set_on_get(on_get)

    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
