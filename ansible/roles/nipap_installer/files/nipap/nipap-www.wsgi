#
# Set up a wsgi environment for mod_wsgi
#

import os, sys

# Add the virtual environment packages to the Python path
sys.path.insert(0, os.path.join('/usr/share/nipap/venv/', 'lib/python3.12/site-packages'))

# Add the directory containing nipapwww to the system path
sys.path.insert(0, '/usr/share/nipap/nipap-www')
sys.path.insert(0, '/usr/share/nipap/pynipap')
sys.path.insert(0, '/usr/share/nipap/nipap')

from nipapwww import create_app

application = create_app()
