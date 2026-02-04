# libraries
import time
from laplace_server.server_lhc import ServerLHC
from laplace_server.protocol import DEVICE_MOTOR


ADDRESS = "tcp://*:5555"


class DummyMotor:
    def __init__(self):
        self.positions = [0.0, 0.0]

    def set_positions(self, positions):
        print(f"[Motor] Moving to {positions}")
        self.positions[0] = positions["0"]
        self.positions[1] = positions["1"]
        # self.positions = list(map(float, positions.values()))
        print(f"here how looks the positions after mapping = {self.positions}")

    def get_data(self):
        return {
            "positions": self.positions,
            "unit": "a.u."
        }


if __name__ == "__main__":

    motor = DummyMotor()

    server = ServerLHC(
        address=ADDRESS,
        freedom=2,
        device=DEVICE_MOTOR,
        data=motor.get_data(),
        name="dummy_motor"
    )
    print(server.address_for_client)

    # callbacks
    def on_position_changed(positions):
        print(f"here how looks like positions = {positions}")
        motor.set_positions(positions)
        server.set_data(motor.get_data())

    server.set_on_position_changed(on_position_changed)

    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
