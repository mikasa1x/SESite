from fabric.contrib.files import append,exists, sed
from fabric.api import env,local,run
import random

REPO_URL= 'git@github.com:TheNorthRem/note.git'

def deploy():
    site_folder = f'/root/sites/{env.host}'
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder,env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)

def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database','static','virtualenv','source'):
        run(f'mkdir -p {site_folder}/{subfolder}')

def _get_latest_source(source_folder):
    if exists(source_folder+'/.git'):
        run(f'cd {source_folder} && git fetch')
    else:
        run(f'git clone {REPO_URL} {source_folder}')

    prefix = "Active code page: 65001\n"
    current_commit = remove_prefix(local("git log -n 1 --format=%H",capture=True))
  

    run(f'cd {source_folder} && git reset --hard "{current_commit}" ')


def _update_settings(source_folder,site_name):
    settings_path = source_folder+ '/notes/settings.py'
    sed(settings_path,"DEBUG = TRUE","DEBUG = False")
    sed(settings_path,'ALLOWED_HOSTS =.+$',f'ALLOWED_HOSTS = ["{site_name}"]')
    secret_key_file = source_folder+ '/notes/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file,f'SECRET_KEY = "{key}"')
    append(settings_path,'\nfrom .secret_key import SECRET_KEY')

def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder+'/../virtualenv'
    if not exists(virtualenv_folder+'/bin/pip'):
        run(f'python3 -m venv {virtualenv_folder}')
    run(f'{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt')

def _update_static_files(source_folder):
    run(
        f'cd {source_folder}'
        ' && ../virtualenv/bin/python manage.py collectstatic --noinput'
    )

def _update_database(source_folder):
    run(
        f'cd {source_folder}'
        ' && ../virtualenv/bin/python manage.py migrate --noinput'
    )

def remove_prefix(input_string):
    if '\n' in input_string:
        return input_string[input_string.rfind('\n')+1:]
    return input_string

if __name__ == "__main__":
    local('fab -f /path/fabfile.py deploy')
