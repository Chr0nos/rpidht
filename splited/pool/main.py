from gevent import monkey; monkey.patch_all()
import gevent
import requests
from huey import SqliteHuey, crontab
from pool.models import Event


huey = SqliteHuey('/tmp/test.sqlite')
mesurement_endpoint = 'http://192.168.1.35:8000/dht/mesurement'


@huey.periodic_task(crontab(minute='*/10'))
def pool_mesurement():
    response = requests.get(mesurement_endpoint)
    assert response.status_code == 200

    response_data = response.json()
    response_data.pop('manager_class', None)
    response_data.pop('id', None)
    event = Event(**response_data)
    print(event)
    event.save()
