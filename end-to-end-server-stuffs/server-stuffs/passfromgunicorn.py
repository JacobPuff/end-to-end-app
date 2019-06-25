testgunicorn = __import__("test-gunicorn")


def passtogunicorn(environ, start_response):
    testgunicorn.gunicornstuffs(environ, start_response)
