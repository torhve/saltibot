import salt.utils.event
import os

class Isea(object):
    def __init__(self):
        self.filters = []
        self.jidsin = []
        self.jidsout = []
    
    def add_filter(self, filter):
        self.filters.append(filter)

    def listen(self, node, socket, callback_func):
        print('Listening with {0} filters'.format(len(self.filters)))

        sock = os.path.join(socket, node)
        event = salt.utils.event.SaltEvent(node, sock)
        
        while True:
            ret = event.get_event(full=True)

            if len(self.jidsin) > 1000:
                self.jidsin.pop()

            if len(self.jidsout) > 10:
                self.jidsout.pop()

            if ret is None:
                continue
            
            data = ret.get('data', False)
            
            if data is None:
                continue
           
            if 'jid' in data.keys():
                if 'return' in data.keys():
                    if (data['jid'], data['id']) in self.jidsin:
                        continue
                    else:
                        self.jidsin.append((data['jid'], data['id']))
                else:
                    if data['jid'] in self.jidsout:
                        continue
                    else:
                        self.jidsout.append(data['jid'])

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
            

