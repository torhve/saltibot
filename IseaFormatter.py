#/usr/bin/env python
# -*- coding: UTF-8

def IseaFormatter(data):
    jid = data['jid']#[12:]
    # Command or return
    if 'return' in data:
        success = 'FAIL!'
        if data['success']:
            success = 'SUCCESS!'
        line = "[{}] {} {} {} {}".format(
                jid,
                data['fun'],
                ','.join(data['fun_args']),
                data['id'],
                success
                )
    else:
        line = "[{}] {} {} {} {}".format(
                jid,
                data['fun'],
                ','.join(data['arg']),
                ','.join(data['minions']),
                data['user']
                )
    return line
