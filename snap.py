import subprocess
from typing import Dict, List

import dotbot


class Snap(dotbot.Plugin):
    _directive = 'snap'

    def can_handle(self, directive: str):
        return self._directive == directive

    def _is_installed(self, name: str):
        cmd = f'snap list | grep -c \'^{name}\\s\''
        result = subprocess.run(
            cmd, shell=True, check=False, stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        return result.returncode == 0

    def handle(self, directive: str, data: List):
        if directive != self._directive:
            raise ValueError(f'snap cannot handle directive {directive}')

        defaults = self._context.defaults().get(self._directive, {})
        classic_defauls = defaults.get("classic", False)

        command_prefix = 'snap install'
        commands = []
        apps = []
        success = True

        for item in data:
            name = item
            is_classic = classic_defauls

            if isinstance(item, Dict):
                name = next(iter(item))
                if name:
                    options = item.get(name)
                    if options:
                        is_classic = options.get('classic', classic_defauls)

            if is_classic:
                if self._is_installed(name):
                    print(f'classic {name} is already installed')
                else:
                    commands.append(f'{command_prefix} --classic {name}')
            else:
                apps.append(name)

        app_list = ''
        for app in apps:
            if self._is_installed(app):
                print(f'{app} is already installed')
            else:
                app_list += f' {app}'

        if app_list:
            commands.append(f'{command_prefix} {app_list}')

        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError:
                success = False

        if success:
            self._log.info('All packages have been installed')
        else:
            self._log.error('Some packages were not successfully installed')

        return success
