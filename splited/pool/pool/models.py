import mongomodel
import json
from tabulate import tabulate
from datetime import datetime, timedelta


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
    pressure = mongomodel.FloatField()

    def __str__(self):
        temp = f'{round(self.temperature, 2)}°C'
        humidity = f'{round(self.humidity, 2)}%'
        date = self.local_date.strftime('%Y-%m-%d %H:%M:%S')
        pressure = f'{round(self.pressure, 2)} hPa' \
            if self.pressure is not None else 'n/a'
        return f'temp: {temp:5} humidity: {humidity:5} pressure: {pressure} ' \
               f' date: {date}'

    @property
    def local_date(self):
        return self.date + timedelta(hours=2)
