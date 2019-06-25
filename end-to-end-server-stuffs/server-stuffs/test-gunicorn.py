def gunicornstuffs(environ, start_response):
    """Simplest possible application object"""
    data = b'get!\n'
    if(environ['REQUEST_METHOD'] == 'POST'):
        data = b'post!\n'
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return iter([data])
