import os
import tempfile
import unittest

from task_store import TaskStore


class TaskStoreTest(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        os.remove(self.path)
        self.store = TaskStore(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_add_ignores_blank(self):
        self.assertIsNone(self.store.add('   '))
        self.assertEqual(self.store.tasks, [])

    def test_add_toggle_persist(self):
        t = self.store.add(' Buy milk ', '2%')
        self.assertEqual(t['title'], 'Buy milk')
        self.store.toggle(t['id'])
        reloaded = TaskStore(self.path)
        self.assertTrue(reloaded.tasks[0]['done'])
        self.assertEqual(reloaded.counts(), (0, 1))

    def test_visible_order_filter_search(self):
        a = self.store.add('a')
        self.store.add('b', notes='find me')
        self.store.toggle(a['id'])
        titles = [t['title'] for t in self.store.visible()]
        self.assertEqual(titles, ['b', 'a'])
        self.assertEqual([t['title'] for t in self.store.visible(show_done=False)], ['b'])
        self.assertEqual([t['title'] for t in self.store.visible(query='FIND')], ['b'])

    def test_update_delete_clear(self):
        a = self.store.add('a')
        b = self.store.add('b')
        self.store.update(a['id'], title='A2', notes='n')
        self.assertEqual(self.store._find(a['id'])['title'], 'A2')
        self.store.update(a['id'], title='  ')  # blank title is ignored
        self.assertEqual(self.store._find(a['id'])['title'], 'A2')
        self.store.toggle(b['id'])
        self.assertEqual(self.store.clear_done(), 1)
        self.store.delete(a['id'])
        self.assertEqual(TaskStore(self.path).tasks, [])

    def test_corrupt_file(self):
        with open(self.path, 'w') as f:
            f.write('{not json')
        self.assertEqual(TaskStore(self.path).tasks, [])


if __name__ == '__main__':
    unittest.main()
