import os
import logging
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from locale import setlocale, LC_NUMERIC
from gi.repository import Notify
from itertools import islice
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

logger = logging.getLogger(__name__)
ext_icon = 'images/icon.png'
directories = []
executables = []
lib_filter = False

def is_library(path):
    """Return True if this looks like a lib file we want to filter out."""
    name   = os.path.basename(path).lower()
    parent = os.path.basename(os.path.dirname(path)).lower()
    # Name enthält "lib" oder endet auf ".so" oder übergeordneter Ordner enthält "lib"
    return (
        'lib' in name or
        '.so' in name or
        'lib' in parent
    )

class ExecLauncherExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesEventListener())
        setlocale(LC_NUMERIC, '')  # set to OS default locale;

    def show_notification(self, title, text=None, icon=ext_icon):
        logger.debug('Show notification: %s' % text)
        icon_full_path = os.path.join(os.path.dirname(__file__), icon)
        Notify.init("ExecutableLauncher")
        Notify.Notification.new(title, text, icon_full_path).show()


class KeywordQueryEventListener(EventListener):

    global directories, executables, lib_filter

    def on_event(self, event, extension):
        return RenderResultListAction(list(islice(self.generate_results(event, extension), 10)))
    
    def generate_results(self, event, extension):
        query = event.get_argument().lower() if event.get_argument() else ""
        executables = [];
        for directory in directories:
            if os.path.isdir(directory):
                for root, dirs, files in os.walk(directory):
                    for filename in files:
                        # Namens-Filter
                        if query and query not in filename.lower():
                            continue

                        path = os.path.join(root, filename)
                        # Nur reguläre Dateien mit X-Bit
                        if not (os.path.isfile(path) and os.access(path, os.X_OK)):
                            continue

                        # Shell-Skripte direkt aufnehmen
                        if filename.lower().endswith('.sh'):
                            executables.append(path)
                            continue

                        # Optionaler Lib-Filter
                        if lib_filter and is_library(path):
                            continue

                        # ELF-Magic prüfen für alles Andere
                        try:
                            with open(path, 'rb') as f:
                                if f.read(4) != b'\x7fELF':
                                    continue
                        except OSError:
                            continue

                        executables.append(path)
        if (len(executables) == 0):
            extension.show_notification("Error", "No executables found in the configured directories", icon=ext_icon)
        if query:
            executables.sort(key=lambda p: (
                not os.path.basename(p).lower().startswith(query),
                os.path.basename(p).lower()
            ))
        else:
            executables.sort(key=lambda p: os.path.basename(p).lower())
        for executable in executables:
            name = os.path.splitext(os.path.basename(executable))[0]
            folder = os.path.basename(os.path.dirname(executable))
            yield ExtensionResultItem(
                icon='images/icon.png',
                name=name,
                description=f'Launch {name} (in ../{folder})',
                on_enter=ExtensionCustomAction(executable)
            )

class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        data = event.get_data()
        os.system(data)


class PreferencesEventListener(EventListener):

    def on_event(self, event, extension):
        global directories
        global lib_filter
        string = ''
        if hasattr(event, 'preferences'):
            string = event.preferences['exec_launcher_directories']
        else:
            if (event.id=='exec_launcher_directories'):
                string = event.new_value
        if string!='':
            directories = []
            list = string.split(',')
            if len(list) == 0:
                extension.show_notification("Error", "No directories found in configuration", icon=ext_icon)
            else:
                home_dir = os.path.expanduser("~")
                for path in list:
                    path = path.strip()
                    if path.startswith("~"):
                        path = path.replace("~", home_dir, 1)
                    if os.path.isdir(path):
                        directories.append(path)
        if hasattr(event, 'preferences'):
            lib_filter = bool(event.preferences.get('exec_launcher_enable_lib_filter', False))
        elif event.id == 'exec_launcher_enable_lib_filter':
             lib_filter = bool(event.new_value)

if __name__ == '__main__':
    ExecLauncherExtension().run()
