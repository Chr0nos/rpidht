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
import json


# tl = TimeLoop()


class EventManager(mongomodel.QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._db.connect(host='192.168.1.41', db='test')

    def showall(self):
        def get_values(event):
            return (
                round(event.temperature, 2),
                round(event.humidity, 2),
                event.local_date
            )

        print(tabulate(
            [get_values(event) for event in self.sort(['date'])],
            headers=('temperature', 'humidity', 'date'),
            tablefmt='pretty'))

    def create_from_sensor(self) -> 'Event':
        assert Adafruit_DHT is not None
        sensor = Adafruit_DHT.AM2302
        pin = 23
        while True:
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
            if temperature is not None and humidity is not None:
                event = self.create(
                    temperature=temperature,
                    humidity=humidity
                )
                return event

    def to_json(self, filepath: str):
        def event_json(event: Event):
            return {
                'date': event.date.timestamp(),
                'tempereature': event.temperature,
                'humidity': event.humidity
            }

        with open(filepath, 'w') as fp:
            json.dump(
                [event_json(event) for event in self.sort(['date'])],
                sort_keys=True,
                indent=4,
                fp=fp
            )


class Event(mongomodel.Document):
    manager_class = EventManager
    temperature = mongomodel.FloatField()
    humidity = mongomodel.FloatField()
    date = mongomodel.DateTimeField(default=lambda: datetime.utcnow())

    def __str__(self):
        temp = f'{round(self.temperature, 2)}°C'
        humidity = f'{round(self.humidity, 2)}%'
        date = self.local_date.strftime('%Y-%m-%d %H:%M:%S')
        return f'temp: {temp:5} humidity: {humidity:5} date: {date}'

    @property
    def local_date(self):
        return self.date + timedelta(hours=2)


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
#     event = Event.objects.create_from_sensor()
#     print(event)


@click.command()
def capture_events():
    # tl.start(block=True)
    try:
        while True:
            with ConsitentWaiter(duration=timedelta(minutes=10)):
                event = Event.objects.create_from_sensor()
                print(event)
    except KeyboardInterrupt:
        print('Exit')


@click.command()
def show_all():
    Event.objects.showall()


@click.command()
@click.option('--last', type=int, default=None, required=False)
def display_graph(last):
    import numpy as np
    from matplotlib import pyplot as plt

    qs = Event.objects.sort(['date'])

    if last is not None:
        now = datetime.now()
        six_hours_ago = now - timedelta(hours=last + 2)
        qs = qs.filter(date__gte=six_hours_ago)

    temperatures = np.array(qs.values_list('temperature', flat=True))
    humidities = np.array(qs.values_list('humidity', flat=True))
    dates = np.array([
        date + timedelta(hours=2) for
        date in qs.values_list('date', flat=True)
    ])

    plt.plot(dates, temperatures, label='Temperature')
    plt.plot(dates, humidities, label='Humidity')
    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.title('Home TH monitoring')
    plt.show()


@click.command()
@click.argument('file')
def export(file):
    Event.objects.to_json(file)


@click.group()
def cli():
    pass


if __name__ == "__main__":
    cli.add_command(capture_events)
    cli.add_command(show_all)
    cli.add_command(display_graph)
    cli.add_command(export)
    cli()
