#/usr/bin/env python
# -*- coding: UTF-8

def IseaFormatter(data):
    jid = data['jid']#[12:]
    # Command or return
    if 'return' in data:
        success = 'FAIL!'
        if data['success']:
            success = 'SUCCESS!'

        if type(data['return']) == type({}):
            ok = 0
            failed = 0
            for k,v in data['return'].items():
                if v['result']:
                    ok += 1
                else:
                    failed += 1
            result = "OK:{} Failed:{}".format(ok, failed)
        else:
            result = data['return']

        fun_args = ''

        if 'fun_args' in data.keys():
            fun_args = data['fun_args']

        line = "\002[{}]\002 {} {} {} {} {}".format(
                jid,
                data['fun'],
                ','.join(fun_args),
                data['id'],
                success,
                result
                )
    else:
        line = "\002[{}]\002 {} {} {} {}".format(
                jid,
                data['fun'],
                ','.join(data['arg']),
                ','.join(data['minions']),
                data['user']
                )
    return line
