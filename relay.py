from typing import List
import RPi.GPIO as GPIO


class Relay:
    def __init__(self, pin):
        self.pin = pin
        self.state = None

    def switch(self, state: bool):
        GPIO.output(self.pin, state)
        self.state = state
        return self

    def __repr__(self):
        return f'<Relay pin {self.pin} ({self.state})>'


class RelayBoard:
    def __init__(self, *relays):
        self.relays = relays

    def __enter__(self, *_):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        return self

    def add(self, relay: Relay):
        self.relays.append(relay)
        return self

    def pins(self) -> List[int]:
        return [relay.pin for relay in self.relays]

    def setup(self):
        GPIO.setup(self.pins, GPIO.OUT, GPIO.HIGH)
        return self

    def __exit__(self, *_):
        GPIO.cleanup()


def setall(state=False):
    relays = [Relay(pin) for pin in (12, 11, 10, 8)]
    with RelayBoard(*relays) as board:
        board.setup()
        for relay in relays:
            relays.switch(state)
