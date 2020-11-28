import click
from pool.models import Event
from datetime import timedelta, datetime


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
        print(f'last {last} hours')
        print('matching items:', qs.count())

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



@click.command()
def show_all():
    Event.objects.showall()


@click.group()
def cli():
    pass


if __name__ == "__main__":
    cli.add_command(show_all)
    cli.add_command(display_graph)
    cli.add_command(export)
    cli()
