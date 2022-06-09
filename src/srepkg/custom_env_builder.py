import subprocess
import venv


class CustomEnvBuilder(venv.EnvBuilder):

    def __init__(self):
        super().__init__(with_pip=True, upgrade_deps=True)
        self._context = None

    @property
    def context(self):
        return self._context

    def post_setup(self, context) -> None:
        subprocess.call([context.env_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])
        subprocess.call([context.env_exe, '-m', 'pip', 'install', 'wheel'])
        self._context = context
