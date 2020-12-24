from flask_script import Manager
from App.app import app, ENV

manager = Manager(app)
if ENV == 'prod':
    app.config['DEBUG'] = False  # Ensure debugger will load.
else:
    app.config['DEBUG'] = True # Ensure debugger will load.

if __name__ == '__main__':
    manager.run()