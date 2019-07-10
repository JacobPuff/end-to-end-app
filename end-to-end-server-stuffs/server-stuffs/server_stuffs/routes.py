def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('api', '/api')
    config.add_route('foobar', '/api/foobar')
