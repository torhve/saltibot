import pprint
from Isea import Isea
from IseaFilter import IseaFilter

def print_data(data):
    pprint.pprint(data)

if __name__ == '__main__':
    print('About to run ISEA test')

    f = IseaFilter('Minions and fun')
    f.add_filter('minions', ['alex-linuxdev-vm'])
    f.add_filter('fun', ['test.ping'])

    f2 = IseaFilter('Fun')
    f2.add_filter('fun', ['grains.items'])

    i = Isea()
    i.add_filter(f)
    i.add_filter(f2)
    i.listen('master', '/var/run/salt', print_data)

