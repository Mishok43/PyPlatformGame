#!/usr/bin/env python3
'''
Dafault: create wheel
'''
import glob
from doit.tools import create_folder

DOIT_CONFIG = {'default_tasks': ['all']}


def task_gitclean():
    """Clean all generated files not tracked by GIT."""
    return {
            'actions': ['git clean -xdf'],
           }


def task_html():
    """Make HTML documentationi."""
    return {
            'actions': ['sphinx-build -M html docs build'],
           }


def task_test():
    """Preform tests."""
    yield {'actions': ['coverage run -m unittest -v'], 'name': "run"}
    yield {'actions': ['coverage report'], 'verbosity': 2, 'name': "report"}


def task_pot():
    """Re-create .pot ."""
    return {
            'actions': ['pybabel extract -o PyPlatformGame.pot PyPlatformGame'],
            'file_dep': glob.glob('PyPlatformGame/*.py'),
            'targets': ['PyPlatformGame.pot'],
           }


def task_po():
    """Update translations."""
    return {
            'actions': ['pybabel update -D PyPlatformGame -d po -i PyPlatformGame.pot'],
            'file_dep': ['PyPlatformGame.pot'],
            'targets': ['po/ru/LC_MESSAGES/PyPlatformGame.po'],
           }


def task_mo():
    """Compile translations."""
    langs = ['en', 'ru']
    return {
            'actions': [
                (create_folder, [f'PyPlatformGame/{lang}/LC_MESSAGES']) for lang in langs
                       ] +
                       [
    f'pybabel compile -D PyPlatformGame -l {lang} -i po/{lang}/LC_MESSAGES/PyPlatformGame.po -d PyPlatformGame' for lang in langs
                       ],
            'file_dep': [
                f'po/{lang}/LC_MESSAGES/PyPlatformGame.po' for lang in langs
                        ],
            'targets': [
                f'PyPlatformGame/{lang}/LC_MESSAGES/PyPlatformGame.mo' for lang in langs
                       ],
           }


def task_sdist():
    """Create source distribution."""
    return {
            'actions': ['python -m build -s'],
            'task_dep': ['gitclean'],
           }


def task_wheel():
    """Create binary wheel distribution."""
    return {
            'actions': ['python -m build -w'],
            'task_dep': ['mo'],
           }


def task_app():
    """Run application."""
    return {
            'actions': ['python -m PyPlatformGame'],
            'task_dep': ['mo'],
           }


def task_style():
    """Check style with pylint."""
    return {
            'actions': ['pylint PyPlatformGame']
           }


def task_docstyle():
    """Check docstrings against pydocstyle."""
    return {
            'actions': ['pydocstyle PyPlatformGame']
           }


def task_check():
    """Perform all checks."""
    return {
            'actions': None,
            'task_dep': ['style', 'docstyle', 'test']
           }


def task_all():
    """Perform all build task."""
    return {
            'actions': None,
            'task_dep': ['check', 'html', 'wheel']
           }