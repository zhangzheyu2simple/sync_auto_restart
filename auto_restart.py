import requests
import json
import time
import os
# import pprint
import random
from collections import Counter
from ts_rpc.client import find_rpc_service,RemoteObject
day_limt = int(os.getenv('SYNC_DAY_LIMIT', '7'))
# url = os.getenv('SYNC_URL', 'http://sync.bj.tusimple.ai:30104/jsonrpc')
iter_min = int(os.getenv('SYNC_ITER_MIN', '10'))
retry_limit = int(os.getenv('SYNC_RETRY_LIMIT', '10'))
retry_counter = Counter()
sync_rpc = RemoteObject('http://sync.bj.tusimple.ai:30104/jsonrpc')

# def _post(url, send_json, timeout=10):

#     resp = requests.post(url, json=send_json, timeout=timeout)
#     jr = json.loads(resp.text)
#     return jr


# def get_fail_task():
#     sendingjson = {'id': None,
#                    'jsonrpc': '2.0',
#                    'method': 'list_task',
#                    'params': [{'displayNum': 15,
#                                'keyword': '',
#                                'pageNum': 0,
#                                'status': ['Fail']}]}
#     return _post(url, sendingjson)
def get_fail_task():
    # sync_rpc = find_rpc_service('sync', 'bj')
    return sync_rpc.list_task({'displayNum': 15,
                               'keyword': '',
                               'pageNum': 0,
                               'status': ['Fail']})


def get_downloading_task():
    # sync_rpc = find_rpc_service('sync', 'bj')
    sync_rpc = RemoteObject('http://sync.bj.tusimple.ai:30104/jsonrpc')

    return sync_rpc.list_task({'displayNum': 15,
                               'keyword': '',
                               'pageNum': 0,
                               'status': ['Downloading', 'Searching', 'Waiting']})
    # sendingjson = {'id': None,
    #                'jsonrpc': '2.0',
    #                'method': 'list_task',
    #                'params': [{'displayNum': 15,
    #                            'keyword': '',
    #                            'pageNum': 0,
    #                            'status': ['Downloading', 'Searching', 'Waiting']}]}

    # return _post(url, sendingjson)


def set_waiting(id, dry_run=False):
    retry_counter[id] += 1
    if dry_run:
        print('dry-run waiting {}'.format(id))
    else:
        print('set waiting {}'.format(id))
        # sync_rpc = find_rpc_service('sync', 'bj')
        return sync_rpc.update_task(id, 'status', 'Waiting')
        # sendingjson = {'id': None,
        #                'jsonrpc': '2.0',
        #                'method': 'update_task',
        #                'params': [id, 'status', 'Waiting']}
        # _post(url, sendingjson)


def not_time_out_filter(t):
    now = time.time()
    # print(now,t['create_at'])
    if now-t['create_at'] < 60*60*24*day_limt:
        return True
    else:
        return False


def not_reach_counter_limit(t):
    if retry_counter[t['id']] < retry_limit:
        return True
    return False


def downloading_task_reach_limit():
    dt = get_downloading_task()
    if dt['numPage'] >= 3:
        return True
    return False


def process():
    if downloading_task_reach_limit():
        print('reach limit')
        time.sleep(60*iter_min)
        return
    jr = get_fail_task()
    res = list(filter(not_time_out_filter, jr['tasks']))
    res = list(filter(not_reach_counter_limit, res))
    if len(res) > 0:
        needed_restart = random.choice(res)
        needed_restart_id = needed_restart['id']
        print('ready to set waiting {}'.format(needed_restart['target']))
        set_waiting(needed_restart_id)
        time.sleep(60*1)
    else:
        time.sleep(60*iter_min)
        print('no suitable task')


if __name__ == "__main__":
    while True:
        try:
            process()
            time.sleep(1)
        except requests.exceptions.Timeout as e:
            print('timeout')
        # process()
