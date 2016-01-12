Integration Tests
=================

The purpose of these tests is to test server functionality
without mocking. These tests are not so much about attaining
code coverage, as they are about ensuring that OmicronServer
"plays nice" with other components.

Test Database Round-Trip
------------------------

    .. automodule:: tests.integration.test_database_roundtrip
        :members:

Test Auth
---------

    .. automodule:: tests.integration.test_auth
        :members:
