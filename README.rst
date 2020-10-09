Coronavirus Dashboard
~~~~~~~~~~~~~~~~~~~~~

This project contains dashboard(s) and other visualizations to monitor the outbreak.

Currently includes:

* A dashboard that detects hotspots based on growth (not total cases) and maps them.

Uses third-party data:

* Coronavirus data from the New York Times.

This is an experimental project. The numbers may be wrong. It should not be relied 
on for any decision making without additional review.

Installation
~~~~~~~~~~~~

:: 

    pip install corona-dashboard


Usage
~~~~~

::

    corona-dashboard up

Running the web app on a WSGI server is recommended for production. The module is 
"corona_dashboard.app:SERVER". We use uWSGI.

License and Acknowledgment
~~~~~~~~~~~~~~~~~~~~~~~~~~

Apache 2. See LICENSE file for details.

A project of `B.Next <https://www.bnext.org/>`_.