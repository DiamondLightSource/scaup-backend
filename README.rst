Scaup API
===========================

|code_ci| |license|

============== ==============================================================
Source code    https://github.com/DiamondLightSource/scaup-backend
============== ==============================================================

Sample Consignment, Administration and User Parametrisation backend

==========
Configuration
==========

The API supports a configuration file, that follows the example set in :code:`config.json`, but most importantly, two environment variables need to be set:

- :code:`SQL_DATABASE_URL`: The URL for the database
- :code:`CONFIG_PATH`: Path for the configuration file
- :code:`SCAUP_PRIVATE_KEY`: Private key for encoding JWTs
- :code:`SCAUP_PUBLIC_KEY`: Public key for decoding JWTs
- :code:`SCAUP_EXPEYE_TOKEN`: Token for making requests to Expeye. Useful for machine users.

==========
Deployment
==========

Running development server on your machine:

1. Install the package with :code:`pip install .` or :code:`pip install -e .`
2. Set the `SQL_DATABASE_URL` environment variable according to your database's location
3. Run :code:`uvicorn` with `uvicorn scaup.main:app --reload --port 8000`

Note: Due to Postgres specific features being used, the target database must be Postgres. An example can be found in the database folder.

============
Testing
============

- Build the database Docker image in `database` with :code:`podman build . -t diamond-ispyb`
- Run with :code:`podman run -p 3306:3306 --detach --name diamond-ispyb localhost/diamond-ispyb`
    - You may change the port or where the container itself runs, just remember to update `.test.env`
- Run :code:`pytest tests`

.. |code_ci| image:: https://gitlab.diamond.ac.uk/lims/scaup-backend/badges/master/pipeline.svg
    :target: https://gitlab.diamond.ac.uk/lims/scaup-backend/-/pipelines
    :alt: Code CI

.. |license| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :target: https://opensource.org/licenses/Apache-2.0
    :alt: Apache License

..
    Anything below this line is used when viewing README.rst and will be replaced
    when included in index.rst
