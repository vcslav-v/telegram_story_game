import redis
from os import environ


r = redis.Redis(
    host=environ.get('REDIS') or 'localhost',
    decode_responses=True,
)


def is_call_to(key: str, expext_val: str):
    return r.hget(key, key='call_to') == expext_val


def is_wait_user(tg_id: int):
    if r.keys(f'wait*:{tg_id}'):
        return True
    return False


def flush_user(tg_id: int):
    for key in r.keys('*:{}'.format(tg_id)):
        r.delete(key)


class UserContext:
    def __init__(self, tg_id: int):
        self.tg_id = tg_id
        self._context_call = f'{tg_id}:context'
        self._status_call = f'{tg_id}:status'
        self._params_call = f'{tg_id}:params'

    def get_context(self, key):
        return r.hget(self._context_call, key)

    def update_context(self, key: str, value: str):
        return r.hset(self._context_call, mapping={key: value})

    def rm_context(self, key):
        return r.hdel(self._context_call, key)

    def flush_context(self):
        return r.delete(self._context_call)

    def get_status(self):
        return r.get(self._status_call)

    def set_status(self, value: str):
        return r.set(self._status_call, value)

    def rm_status(self):
        return r.delete(self._status_call)

    def get_params(self):
        return r.hgetall(self._params_call)

    def set_params(self, params: dict):
        r.delete(self._params_call)
        return r.hset(self._params_call, mapping=params)

    def flush_all(self):
        for key in r.keys('{}:*'.format(self.tg_id)):
            r.delete(key)
