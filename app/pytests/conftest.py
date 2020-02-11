
def pytest_addoption(parser):
    parser.addoption('--repeat', action='store',
                     help='Number of times to repeat each test')