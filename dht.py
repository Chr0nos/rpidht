#!env python3
try:
    import Adafruit_DHT
except ModuleNotFoundError:
    Adafruit_DHT = None
import mongomodel
from datetime import datetime, timedelta
from time import sleep
from tabulate import tabulate
# from timeloop import TimeLoop
import click


# tl = TimeLoop()


class Event(mongomodel.Document):
    temperature = mongomodel.FloatField()
    humidity = mongomodel.FloatField()
    date = mongomodel.DateTimeField(default=lambda: datetime.now())

    @classmethod
    def new(cls) -> 'Event':
        assert Adafruit_DHT is not None
        sensor = Adafruit_DHT.AM2302
        pin = 23
        while True:
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
            if temperature is not None and humidity is not None:
                event = cls(temperature=temperature, humidity=humidity)
                return event

    def __str__(self):
        temp = f'{round(self.temperature, 2)}°C'
        humidity = f'{round(self.humidity, 2)}%'
        date = (self.date + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        return f'temp: {temp:5} humidity: {humidity:5} date: {date}'

    @classmethod
    def showall(cls):
        def get_values(event):
            return (
                round(event.temperature, 2),
                round(event.humidity, 2),
                event.date + timedelta(hours=2)
            )

        print(tabulate(
            [get_values(event) for event in cls.objects.sort(['date'])],
            headers=('temperature', 'humidity', 'date'),
            tablefmt='pretty'))


@click.group()
def cli():
    pass


class ConsitentWaiter:
    """This context manager waits for a consitent time regarding to the task
    it runs duration time.
    """
    def __init__(self, duration: timedelta):
        self.duration = duration

    def __enter__(self, *_):
        self.reset()

    def reset(self):
        self.started = datetime.now()

    def __exit__(self, *_):
        elapsed = datetime.now() - self.started
        time_to_wait = self.duration - elapsed
        # print('waiting for', time_to_wait)
        sleep(time_to_wait.total_seconds())


# @tl.job(timedelta(minutes=10))
# def create_new_event():
#     event = Event.new()
#     event.save()
#     print(event)


@click.command()
def capture_events():
    # tl.start(block=True)
    try:
        while True:
            with ConsitentWaiter(duration=timedelta(minutes=10)):
                event = Event.new()
                event.save()
                print(event)
    except KeyboardInterrupt:
        print('Exit')


@click.command()
def show_all():
    Event.showall()


@click.command()
def display_graph():
    import numpy as np
    from matplotlib import pyplot as plt

    qs = Event.objects.sort(['date'])
    temperatures = np.array([event.temperature for event in qs])
    humidities = np.array([event.humidity for event in qs])
    dates = np.array([event.date + timedelta(hours=2) for event in qs])

    plt.plot(dates, temperatures, label='Temperature')
    plt.plot(dates, humidities, label='Humidity')
    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.title('Home TH monitoring')
    plt.show()


if __name__ == "__main__":
    mongomodel.database.connect(host='192.168.1.41', db='test')

    cli.add_command(capture_events)
    cli.add_command(show_all)
    cli.add_command(display_graph)
    cli()
