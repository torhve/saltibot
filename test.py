import pprint
from Isea import Isea
from IseaFilter import IseaFilter
from IseaFormatter import IseaFormatter

def print_data(data):
    pprint.pprint(data)

if __name__ == '__main__':
    print('About to run ISEA test')

    def output(data):
         print('{}'.format(IseaFormatter(data)))

    isea = Isea()
    f2 = IseaFilter('Fun')
    f2.add_filter('fun', ['state.sls','test.ping', 'test.version', 'state.highstate'])
    isea.add_filter(f2)
    isea.listen('master', '/var/run/salt', output)
