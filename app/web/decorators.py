from aiohttp.web_exceptions import HTTPUnauthorized


def require_auth(func):
    async def require_auth_wrap(self, *args, **kwargs):
        if not self.request.admin:
            raise HTTPUnauthorized(text='{"auth": ["You is unauthorized."]}')
        return await func(self, *args, **kwargs)

    return require_auth_wrap
