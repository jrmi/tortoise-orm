from tortoise.backends.base.config_generator import expand_db_url, generate_config
from tortoise.contrib import test
from tortoise.exceptions import ConfigurationError


class TestConfigGenerator(test.SimpleTestCase):

    def test_unknown_scheme(self):
        with self.assertRaises(ConfigurationError):
            expand_db_url('moo://baa')

    def test_sqlite_basic(self):
        res = expand_db_url('sqlite:///some/test.sqlite')
        self.assertDictEqual(res, {
            'engine': 'tortoise.backends.sqlite',
            'credentials': {
                'file_path': '/some/test.sqlite',
            }
        })

    def test_sqlite_relative(self):
        res = expand_db_url('sqlite://test.sqlite')
        self.assertDictEqual(res, {
            'engine': 'tortoise.backends.sqlite',
            'credentials': {
                'file_path': 'test.sqlite',
            }
        })

    def test_sqlite_testing(self):
        res = expand_db_url(
            db_url='sqlite:///some/test-{}.sqlite',
            testing=True,
        )
        file_path = res['credentials']['file_path']
        self.assertIn('/some/test-', file_path)
        self.assertIn('.sqlite', file_path)
        self.assertNotEqual('sqlite:///some/test-{}.sqlite', file_path)
        self.assertDictEqual(res, {
            'engine': 'tortoise.backends.sqlite',
            'credentials': {
                'file_path': file_path,
            }
        })

    def test_sqlite_params(self):
        res = expand_db_url('sqlite:///some/test.sqlite?AHA=5&moo=yes')
        self.assertDictEqual(res, {
            'engine': 'tortoise.backends.sqlite',
            'credentials': {
                'file_path': '/some/test.sqlite',
                'AHA': '5',
                'moo': 'yes',
            }
        })

    def test_sqlite_invalid(self):
        with self.assertRaises(ConfigurationError):
            expand_db_url('sqlite://')

    def test_postgres_basic(self):
        res = expand_db_url('postgres://postgres:@127.0.0.1:5432/test')
        self.assertDictEqual(res, {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'database': 'test',
                'host': '127.0.0.1',
                'password': '',
                'port': '5432',
                'user': 'postgres',
            }
        })

    def test_postgres_nonint_port(self):
        with self.assertRaises(ConfigurationError):
            expand_db_url('postgres://postgres:@127.0.0.1:moo/test')

    def test_postgres_testing(self):
        res = expand_db_url(
            db_url=r'postgres://postgres:@127.0.0.1:5432/test_\{\}',
            testing=True,
        )
        database = res['credentials']['database']
        self.assertIn('test_', database)
        self.assertNotEqual('test_{}', database)
        self.assertDictEqual(res, {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'database': database,
                'host': '127.0.0.1',
                'password': '',
                'port': '5432',
                'user': 'postgres',
            }
        })

    def test_postgres_params(self):
        res = expand_db_url('postgres://postgres:@127.0.0.1:5432/test?AHA=5&moo=yes')
        self.assertDictEqual(res, {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'database': 'test',
                'host': '127.0.0.1',
                'password': '',
                'port': '5432',
                'user': 'postgres',
                'AHA': '5',
                'moo': 'yes',
            }
        })

    def test_mysql_basic(self):
        res = expand_db_url('mysql://root:@127.0.0.1:3306/test')
        self.assertEqual(res, {
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                'database': 'test',
                'host': '127.0.0.1',
                'password': '',
                'port': '3306',
                'user': 'root',
            }
        })

    def test_mysql_nonint_port(self):
        with self.assertRaises(ConfigurationError):
            expand_db_url('mysql://root:@127.0.0.1:moo/test')

    def test_mysql_testing(self):
        res = expand_db_url(r'mysql://root:@127.0.0.1:3306/test_\{\}', testing=True)
        self.assertIn('test_', res['credentials']['database'])
        self.assertNotEqual('test_{}', res['credentials']['database'])
        self.assertEqual(res, {
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                'database': res['credentials']['database'],
                'host': '127.0.0.1',
                'password': '',
                'port': '3306',
                'user': 'root',
            }
        })

    def test_mysql_params(self):
        res = expand_db_url('mysql://root:@127.0.0.1:3306/test?AHA=5&moo=yes')
        self.assertEqual(res, {
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                'database': 'test',
                'host': '127.0.0.1',
                'password': '',
                'port': '3306',
                'user': 'root',
                'AHA': '5',
                'moo': 'yes',
            }
        })

    def test_generate_config_basic(self):
        res = generate_config(
            db_url='sqlite:///some/test.sqlite',
            app_modules={
                'models': [
                    'one.models',
                    'two.models'
                ]
            }
        )
        self.assertEqual(res, {
            'connections': {
                'default': {
                    'credentials': {
                        'file_path': '/some/test.sqlite'
                    },
                    'engine': 'tortoise.backends.sqlite'
                }
            },
            'apps': {
                'models': {
                    'models': [
                        'one.models',
                        'two.models'
                    ],
                    'default_connection': 'default'
                }
            },
        })

    def test_generate_config_explicit(self):
        res = generate_config(
            db_url='sqlite:///some/test.sqlite',
            app_modules={
                'models': [
                    'one.models',
                    'two.models'
                ]
            },
            connection_label='models',
            testing=True
        )
        self.assertEqual(res, {
            'connections': {
                'models': {
                    'credentials': {
                        'file_path': '/some/test.sqlite',
                    },
                    'engine': 'tortoise.backends.sqlite'
                }
            },
            'apps': {
                'models': {
                    'models': [
                        'one.models',
                        'two.models'
                    ],
                    'default_connection': 'models'
                }
            },
        })

    def test_generate_config_many_apps(self):
        res = generate_config(
            db_url='sqlite:///some/test.sqlite',
            app_modules={
                'models': [
                    'one.models',
                    'two.models'
                ],
                'peanuts': [
                    'peanut.models'
                ]
            }
        )
        self.assertEqual(res, {
            'connections': {
                'default': {
                    'credentials': {
                        'file_path': '/some/test.sqlite'
                    },
                    'engine': 'tortoise.backends.sqlite'
                }
            },
            'apps': {
                'models': {
                    'models': [
                        'one.models',
                        'two.models'
                    ],
                    'default_connection': 'default'
                },
                'peanuts': {
                    'models': [
                        'peanut.models'
                    ],
                    'default_connection': 'default'
                }
            }
        })
