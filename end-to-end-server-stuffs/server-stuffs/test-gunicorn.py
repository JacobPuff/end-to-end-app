def gunicornstuffs(environ, start_response):
    """Simplest possible application object"""
    data = bytes("request method is: " + environ['REQUEST_METHOD'] + "!", encoding='utf8')
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return iter([data])
