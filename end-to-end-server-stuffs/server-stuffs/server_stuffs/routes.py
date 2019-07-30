def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('api', '/api')
    config.add_route('tasklists', '/api/tasklists')
    config.add_route('tasklists_by_id', '/api/tasklists/{list_id:.*}')
    config.add_route('tasks', '/api/tasks')
    config.add_route('tasks_by_id', '/api/tasks/{task_id:.*}')
    config.add_route('foobar', '/api/foobar')
