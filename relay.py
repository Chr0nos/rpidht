from typing import List
import RPi.GPIO as GPIO


class Relay:
    def __init__(self, pin):
        self.pin = pin
        self.state = None

    def switch(self, state: bool):
        GPIO.output(self.pin, state is False)
        self.state = state
        return self

    def __repr__(self):
        return f'<Relay pin {self.pin} ({self.state})>'


class Board:
    def __init__(self, *relays):
        self.relays = relays
        self.clean = False

    def __enter__(self, *_):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        return self

    def add(self, relay: Relay):
        self.relays.append(relay)
        return self

    @property
    def pins(self) -> List[int]:
        return list([relay.pin for relay in self.relays])

    def setup(self, clean=False):
        self.clean = clean
        GPIO.setup(self.pins, GPIO.OUT, initial=GPIO.HIGH)
        return self

    def __iter__(self):
        for relay in self.relays:
            yield relay

    def __exit__(self, *_):
        if self.clean:
            GPIO.cleanup()


def setall(state=False):
    relays = [Relay(pin) for pin in (12, 11, 10, 8)]
    with Board(*relays) as board:
        board.setup()
        for relay in board:
            relay.switch(state)
