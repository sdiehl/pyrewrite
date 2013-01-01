from distutils.core import setup

setup(
    name = "pyrewrite",
    license = "BSD",
    description = "Python term rewriting",
    packages = ['rewrite',
                'rewrite.tests'],
    version = "dev",
    #entry_points={
    #    'console_scripts':
    #    ['pyrewrite = rewrite.dsl.cli:main']
    #}
)
