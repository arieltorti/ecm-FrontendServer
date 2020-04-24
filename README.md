SIR Simulation Flask
====================================

Simple server to serve a frontend to the simulation engine build in Flask and VueJS.

Requirements
------------------------

- Python 3
- Flask
- CMS ([https://institutefordiseasemodeling.github.io/Documentation/cms/cms-installation.html](https://institutefordiseasemodeling.github.io/Documentation/cms/cms-installation.html))

Running on development
------------------------
By default flask will look for CMS on "compartments/compartments.exe" based on the server root folder.

    $ pip install flask
    $ FLASK_ENV=development
    $ flask run
