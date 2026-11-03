"""Plain-Python storage layer for the Tasks app (no Pythonista imports,
so it can be tested on any machine)."""
import json
import os
import time
import uuid

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks.json')


class TaskStore(object):
    def __init__(self, path=DEFAULT_PATH):
        self.path = path
        self.tasks = []
        self.load()

    # --- persistence -------------------------------------------------------
    def load(self):
        try:
            with open(self.path, 'r') as f:
                data = json.load(f)
            self.tasks = [t for t in data if isinstance(t, dict) and 'title' in t]
        except (IOError, OSError, ValueError):
            self.tasks = []

    def save(self):
        tmp = self.path + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(self.tasks, f, indent=2)
        os.replace(tmp, self.path)

    # --- queries -----------------------------------------------------------
    def visible(self, show_done=True, query=''):
        """Open tasks first (newest first), then completed ones."""
        q = query.strip().lower()
        items = [t for t in self.tasks
                 if (show_done or not t['done'])
                 and (not q or q in t['title'].lower() or q in t.get('notes', '').lower())]
        return sorted(items, key=lambda t: (t['done'], -t['created']))

    def counts(self):
        done = sum(1 for t in self.tasks if t['done'])
        return len(self.tasks) - done, done

    # --- mutations ---------------------------------------------------------
    def add(self, title, notes=''):
        title = title.strip()
        if not title:
            return None
        task = {'id': uuid.uuid4().hex, 'title': title, 'notes': notes.strip(),
                'done': False, 'created': time.time()}
        self.tasks.append(task)
        self.save()
        return task

    def _find(self, task_id):
        for t in self.tasks:
            if t['id'] == task_id:
                return t
        raise KeyError(task_id)

    def toggle(self, task_id):
        t = self._find(task_id)
        t['done'] = not t['done']
        self.save()
        return t

    def update(self, task_id, title=None, notes=None):
        t = self._find(task_id)
        if title is not None and title.strip():
            t['title'] = title.strip()
        if notes is not None:
            t['notes'] = notes.strip()
        self.save()
        return t

    def delete(self, task_id):
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        self.save()

    def clear_done(self):
        n = sum(1 for t in self.tasks if t['done'])
        self.tasks = [t for t in self.tasks if not t['done']]
        self.save()
        return n
