import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    UPLOAD_FOLDER = basedir + '/app/static/client/uploads'
    ALLOWED_EXTENSIONS = {'obj', 'obja'}
    OBJ_FOLDER = basedir + "/app/static/client/obj"
    AVAILABLE_MODELS = {'icosphere': {'file': 'icosphere.obj',
                                      'watertight': True,
                                      'manifoldness': 1,
                                      'faces': 1280,
                                      'vertices': 642},
                        'sphere': {'file': 'sphere.obj',
                                   'watertight': True,
                                   'manifoldness': 1,
                                   'faces': 4680,
                                   'vertices': 2342},
                        'bunny': {'file': 'bunny.obj',
                                  'watertight': False,
                                  'manifoldness': 1,
                                  'faces': 4968,
                                  'vertices': 2503},
                        'cow': {'file': 'cow.obj',
                                'watertight': True,
                                'manifoldness': 1,
                                'faces': 5804,
                                'vertices': 2903},
                        'suzanne': {'file': 'suzanne.obj',
                                    'watertight': False,
                                    'manifoldness': 3,
                                    'faces': 15488,
                                    'vertices': 7830},
                        'fandisk': {'file': 'fandisk.obj',
                                    'watertight': True,
                                    'manifoldness': 1,
                                    'faces': 19724,
                                    'vertices': 9864},
                        'pokemon': {'file': 'pokemon.obj',
                                    'watertight': True,
                                    'manifoldness': 3,
                                    'faces': 51663,
                                    'vertices': 25926},
                        'hippo': {'file': 'hippo.obj',
                                  'watertight': True,
                                  'manifoldness': 1,
                                  'faces': 64244,
                                  'vertices': 32144}
                        }

    TAUX_ACC = 0.9
    DIST_COMP = 0.01
