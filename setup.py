from distutils.core import setup

setup(
    name = "pyrewrite",
    license = "BSD",
    author='Continuum Analytics',
    author_email='blaze-dev@continuum.io',
    description = "Python term rewriting",
    packages = ['rewrite',
                'rewrite.tests'],
    version = "dev",
    #entry_points={
    #    'console_scripts':
    #    ['pyrewrite = rewrite.dsl.cli:main']
    #}
)
