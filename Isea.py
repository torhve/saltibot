import salt.utils.event
import pprint
import os

class Isea(object):
    filters = []

    def add_filter(self, filter):
        self.filters.append(filter)

    def listen(self, node, socket, callback_func):
        print('Listening with {0} filters'.format(len(self.filters)))

        sock = os.path.join(socket, node)
        event = salt.utils.event.SaltEvent(node, sock)
        
        while True:
            ret = event.get_event(full=True)
            
            if ret is None:
                continue
            
            data = ret.get('data', False)

            if data is None:
                continue
            
            has_returned = False

            for f in self.filters:
                return_data = True
                for k in f.get_filter().keys():
                    if k in data.keys():
                        if isinstance(data[k], basestring):
                            if data[k] in f.get_filter()[k]:
                                return_data = return_data and True
                            else:
                                return_data = False
                        else:
                            if set(f.get_filter()[k]).issubset(set(data[k])):
                                return_data = return_data and True
                            else:
                                return_data = False
                    else:
                        return_data = False

                if not has_returned: 
                    if return_data is True:
                        callback_func(data)
                        has_returned = True
            

