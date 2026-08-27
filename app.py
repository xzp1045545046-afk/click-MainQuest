import json
import os
import sys
import logging
import webview

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
HTML_FILE = os.path.join(BASE_DIR, 'todolist-dnf.html')
LOG_FILE = os.path.join(BASE_DIR, 'app.log')
LOCK_FILE = os.path.join(BASE_DIR, 'app.lock')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

def ensure_dir(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def default_data():
    return {'todos': [], 'avatar': None}


class Api:
    def load_data(self):
        """Load app data from local JSON file."""
        if not os.path.exists(DATA_FILE):
            return default_data()
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                raw = f.read().strip()
                if not raw:
                    return default_data()
                data = json.loads(raw)
                if not isinstance(data, dict):
                    return default_data()
                if 'todos' not in data or not isinstance(data['todos'], list):
                    data['todos'] = []
                if 'avatar' not in data:
                    data['avatar'] = None
                return data
        except Exception as e:
            logging.error('load_data error: %s', e)
            return default_data()

    def save_data(self, data):
        """Save app data to local JSON file."""
        try:
            logging.info('save_data called with %d todos', len(data.get('todos', [])) if isinstance(data, dict) else 0)
            if not isinstance(data, dict):
                data = default_data()
            if 'todos' not in data or not isinstance(data['todos'], list):
                data['todos'] = []
            if 'avatar' not in data:
                data['avatar'] = None
            ensure_dir(DATA_FILE)
            tmp = DATA_FILE + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, DATA_FILE)
            return True
        except Exception as e:
            logging.error('save_data error: %s', e)
            return False

    def _active_window(self):
        """Return the currently active pywebview window, or None."""
        try:
            return webview.active_window()
        except Exception:
            return None

    def save_backup(self, data):
        """Let user pick a .json file and write data to it."""
        try:
            win = self._active_window()
            if win is None:
                return {'ok': False, 'reason': 'no_active_window'}
            from datetime import datetime
            suggested = f'任务手册备份_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
            result = win.create_file_dialog(
                dialog_type=webview.SAVE_DIALOG,
                directory=BASE_DIR,
                save_filename=suggested,
                file_types=('JSON files (*.json)', 'All files (*.*)')
            )
            if not result:
                return {'ok': False, 'reason': 'cancelled'}
            path = result[0] if isinstance(result, (tuple, list)) else result
            if not path:
                return {'ok': False, 'reason': 'cancelled'}
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return {'ok': True, 'path': path}
        except Exception as e:
            logging.error('save_backup error: %s', e)
            return {'ok': False, 'reason': str(e)}

    def load_backup(self):
        """Let user pick a .json file and return its contents."""
        try:
            win = self._active_window()
            if win is None:
                return {'ok': False, 'reason': 'no_active_window'}
            result = win.create_file_dialog(
                dialog_type=webview.OPEN_DIALOG,
                directory=BASE_DIR,
                allow_multiple=False,
                file_types=('JSON files (*.json)', 'All files (*.*)')
            )
            if not result:
                return {'ok': False, 'reason': 'cancelled'}
            path = result[0] if isinstance(result, (tuple, list)) else result
            if not path or not os.path.exists(path):
                return {'ok': False, 'reason': 'not_found'}
            with open(path, 'r', encoding='utf-8') as f:
                raw = f.read().strip()
                if not raw:
                    return {'ok': False, 'reason': 'empty'}
                data = json.loads(raw)
                if not isinstance(data, dict):
                    return {'ok': False, 'reason': 'invalid_format'}
                if 'todos' not in data or not isinstance(data['todos'], list):
                    data['todos'] = []
                if 'avatar' not in data:
                    data['avatar'] = None
                return {'ok': True, 'data': data}
        except Exception as e:
            logging.error('load_backup error: %s', e)
            return {'ok': False, 'reason': str(e)}


api = Api()


class SingleInstanceLock:
    """Cross-platform single-instance lock using a lock file.

    Windows uses msvcrt.locking; macOS/Linux use fcntl.flock.
    The lock is released automatically when the file handle is closed.
    """

    def __init__(self, path):
        self.path = path
        self.fd = None

    def acquire(self):
        try:
            ensure_dir(self.path)
            self.fd = open(self.path, 'w')
            self.fd.write(str(os.getpid()))
            self.fd.flush()
            if sys.platform == 'win32':
                import msvcrt
                msvcrt.locking(self.fd.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (IOError, OSError):
            if self.fd:
                try:
                    self.fd.close()
                except Exception:
                    pass
                self.fd = None
            return False
        except Exception as e:
            logging.error('single_instance_lock error: %s', e)
            return False

    def release(self):
        if self.fd:
            try:
                self.fd.close()
            except Exception:
                pass
            self.fd = None


def main():
    lock = SingleInstanceLock(LOCK_FILE)
    if not lock.acquire():
        logging.warning('Another instance is already running. Exiting.')
        print('Another instance of 任务手册 is already running.', file=sys.stderr)
        sys.exit(0)

    try:
        if not os.path.exists(HTML_FILE):
            logging.error('HTML file not found: %s', HTML_FILE)
            sys.exit(1)

        logging.info('Starting 任务手册 desktop app.')
        window = webview.create_window(
            title='任务手册',
            url=HTML_FILE,
            js_api=api,
            width=1280,
            height=800,
            min_size=(900, 600),
            resizable=True,
            text_select=True
        )
        webview.start(debug=False)
    except Exception as e:
        logging.exception('Fatal error in main: %s', e)
        raise
    finally:
        lock.release()
        logging.info('任务手册 exited.')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.exception('Uncaught exception: %s', e)
        sys.exit(1)
