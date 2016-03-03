__author__ = 'xuanlin'
routers = dict(
    BASE = dict(
        default_application='Grism',
        default_controller='grism',
    ),
)

routes_onerror = [('*/404', 'index'),
                  ('*/*', 'index')]
