""" Cornice services.
"""
from cornice import Service


hello = Service(name='hello', path='/api/hello', description="Simplest app")
more = Service(name='more', path='/api/more', description="Data for Jacob")


@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    return {'d': {'Hello': 'World'}}

@more.get()
def get_more(request):
    """Purely for Jacob's testing'"""
    return {'d': [{'thing_id': 1,
                   'value': 'this is a thing',
                   'stuff': 'I could put more here'
                   },
                   {'thing_id': 345,
                    'value': 'this is another thing',
                    'stuff': 'but I did not put more here',
                    }
                  ]}
