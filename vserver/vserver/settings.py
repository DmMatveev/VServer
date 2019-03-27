import logging.config

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'worker': {
            'handlers': ['default'],
            'level': 'DEBUG',
        },

        'workers': {
            'handlers': ['default'],
            'level': 'DEBUG',
        },
    }
})

RABBIT_HOST = '212.109.195.39'
RABBIT_PORT = '5672'
RABBIT_LOGIN = 'guest'
RABBIT_PASSWORD = 'guest'

REST_IP = '212.109.195.39'
REST_PORT = '8000'

REDIS_IP = '212.109.195.39'

INTERVAL_UPDATE_WORKERS = 60
