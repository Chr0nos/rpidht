from timeloop import Timeloop
from datetime import timedelta, datetime
import requests

from pool.models import Event

tl = Timeloop()


@tl.job(interval=timedelta(minutes=10))
def read_mesurement():
    response = requests.get('http://192.168.1.35:8000/dht/mesurement')
    assert response.status_code == 200
    response = response.json()
    response.pop('date', None)
    response.pop('manager_class', None)
    event = Event(**response)
    event.save()
    print(event)


if __name__ == '__main__':
    read_mesurement()
    tl.start(block=True)
