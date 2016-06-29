campus-textbook
===============

Website for listing textbooks for sale across a campus

## Getting started

First, install `python 3` and `pip`. Then you can set up a virtual environment for this project:

    pip install virtualenv
    virtualenv env
    source env/bin/activate
    python setup.py develop

Then you need to get the javascript dependencies and assets installed. We use grunt for this. First, make sure you have npm installed. Then you need to install two global packages (you may need sudo):

    npm install -g bower grunt-cli

Then you can use grunt to install the remaining dependencies.

    cd path/to/campus-textbook/
    npm install
    grunt

Now you should be all set to start work. You can serve the development version of the site with

    pserve --reload development.ini

(The `--reload` option isn't required, but tells it to automatically reload the site so you can see your changes without restarting the server.)
Finally, go to `http:localhost:6543` to view it.
