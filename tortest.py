import pprint
from Isea import Isea
from IseaFilter import IseaFilter
from IseaFormatter import IseaFormatter


def printer(d):
    print (IseaFormatter(d))
    

if __name__ == '__main__':
    print('About to run ISEA test')


    f2 = IseaFilter('Fun')
    f2.add_filter('fun', ['test.version'])

    i = Isea()
    i.add_filter(f2)
    i.listen('master', '/var/run/salt', printer)

