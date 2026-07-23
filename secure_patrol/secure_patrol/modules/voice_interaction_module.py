import logging
import serial
import time

logger = logging.getLogger("voice")


class VoiceInteractionModule:
    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate
        try:
            self.connection = serial.Serial(port=port, baudrate=baudrate, timeout=3)
            logger.info(f"Voice module connected at {self.port}")
        except Exception as e:
            raise ConnectionError(
                f"{self} port not found. Use 'ls /dev/ttyUSB*' or 'ls /dev/my*' to find ports."
            ) from e

    def write(self, cmd: int) -> None:
        """Write a command to the voice interaction module.

        Writing a command makes the module speak an associated phrase.
        """
        self.connection.write(bytes([0xAA, 0x55, 0x00, cmd, 0xFB]))
        time.sleep(0.005)
        self.connection.reset_input_buffer()

    def read(self) -> int | None:
        """Read the command received from the voice interaction module.

        Refer to the voice command tutorial in
        https://github.com/YahboomTechnology/ROSMASTERX3/tree/main
        for detailed list of commands used.
        """
        # each response is 5 bytes long
        if self.connection.in_waiting < 5:
            return None
        data = self.connection.read(self.connection.in_waiting)
        for i in range(len(data) - 4):
            # check if response is read correctly
            if (
                data[i] == 0xAA
                and data[i + 1] == 0x55
                and data[i + 2] == 0x00
                and data[i + 4] == 0xFB
            ):
                self.connection.reset_input_buffer()
                time.sleep(0.005)
                return int(data[i + 3])
        return None

    def disconnect(self) -> None:
        """Close the serial connection."""
        self.connection.close()
        logger.info(f"Voice module disconnected at {self.port}")
