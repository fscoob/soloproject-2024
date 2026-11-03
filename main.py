"""Tasks — a to-do list app for Pythonista 3 (iOS).

Run this file in Pythonista. Tap a task to check it off, tap the (i) button
to edit it, swipe left to delete. Tasks are saved to tasks.json next to
this script.
"""
import ui
import console
import dialogs

from task_store import TaskStore

ACCENT = '#007aff'


class TaskListView(ui.View):
    def __init__(self, store):
        self.store = store
        self.show_done = True
        self.query = ''
        self.rows = []
        self.name = 'Tasks'
        self.background_color = 'white'

        # Search field
        self.search = ui.TextField(placeholder='Search', clear_button_mode='while_editing',
                                   autocapitalization_type=ui.AUTOCAPITALIZE_NONE,
                                   bordered=True, delegate=self)
        self.search.action = self.search_changed
        self.add_subview(self.search)

        # Quick-add field + button
        self.entry = ui.TextField(placeholder='New task…', delegate=self, bordered=True)
        self.add_subview(self.entry)
        self.add_btn = ui.Button(title='Add', tint_color='white', background_color=ACCENT,
                                 corner_radius=6, font=('<system-bold>', 16))
        self.add_btn.action = self.quick_add
        self.add_subview(self.add_btn)

        # Task table
        self.table = ui.TableView(data_source=self, delegate=self, row_height=56)
        self.add_subview(self.table)

        # Footer with counts
        self.footer = ui.Label(alignment=ui.ALIGN_CENTER, text_color='#888',
                               font=('<system>', 13))
        self.add_subview(self.footer)

        # Navigation bar buttons
        self.right_button_items = [ui.ButtonItem(title='New', action=self.new_task_dialog)]
        self.left_button_items = [ui.ButtonItem(title='Options', action=self.show_options)]

        self.reload()

    # --- layout ------------------------------------------------------------
    def layout(self):
        w, h, pad = self.width, self.height, 10
        self.search.frame = (pad, pad, w - 2 * pad, 34)
        self.entry.frame = (pad, 54, w - 3 * pad - 64, 38)
        self.add_btn.frame = (w - pad - 64, 54, 64, 38)
        self.table.frame = (0, 102, w, h - 102 - 30)
        self.footer.frame = (0, h - 30, w, 30)

    # --- data --------------------------------------------------------------
    def reload(self):
        self.rows = self.store.visible(self.show_done, self.query)
        self.table.reload_data()
        open_n, done_n = self.store.counts()
        self.footer.text = '%d open · %d done' % (open_n, done_n)

    # --- actions -----------------------------------------------------------
    def quick_add(self, sender=None):
        if self.store.add(self.entry.text or ''):
            self.entry.text = ''
            self.reload()

    def search_changed(self, sender):
        self.query = sender.text or ''
        self.reload()

    def new_task_dialog(self, sender=None):
        result = dialogs.form_dialog('New Task', [
            {'type': 'text', 'key': 'title', 'title': 'Title', 'placeholder': 'What needs doing?'},
            {'type': 'text', 'key': 'notes', 'title': 'Notes', 'placeholder': 'Optional'},
        ])
        if result and self.store.add(result.get('title', ''), result.get('notes', '')):
            self.reload()

    def edit_task(self, task):
        result = dialogs.form_dialog('Edit Task', [
            {'type': 'text', 'key': 'title', 'title': 'Title', 'value': task['title']},
            {'type': 'text', 'key': 'notes', 'title': 'Notes', 'value': task.get('notes', '')},
            {'type': 'switch', 'key': 'done', 'title': 'Completed', 'value': task['done']},
        ])
        if result:
            self.store.update(task['id'], result.get('title'), result.get('notes'))
            if bool(result.get('done')) != task['done']:
                self.store.toggle(task['id'])
            self.reload()

    def show_options(self, sender=None):
        toggle_label = 'Hide Completed' if self.show_done else 'Show Completed'
        choice = dialogs.list_dialog('Options', [toggle_label, 'Clear Completed'])
        if choice == toggle_label:
            self.show_done = not self.show_done
            self.reload()
        elif choice == 'Clear Completed':
            try:
                console.alert('Clear Completed', 'Delete all completed tasks?', 'Delete')
            except KeyboardInterrupt:
                return
            n = self.store.clear_done()
            self.reload()
            console.hud_alert('Removed %d task%s' % (n, '' if n == 1 else 's'))

    # --- TextField delegate -----------------------------------------------
    def textfield_should_return(self, textfield):
        if textfield is self.entry:
            self.quick_add()
        textfield.end_editing()
        return True

    def textfield_did_change(self, textfield):
        if textfield is self.search:
            self.search_changed(textfield)

    # --- TableView data source --------------------------------------------
    def tableview_number_of_sections(self, tableview):
        return 1

    def tableview_number_of_rows(self, tableview, section):
        return len(self.rows)

    def tableview_cell_for_row(self, tableview, section, row):
        task = self.rows[row]
        cell = ui.TableViewCell('subtitle')
        mark = u'☑  ' if task['done'] else u'☐  '
        cell.text_label.text = mark + task['title']
        cell.text_label.text_color = '#999' if task['done'] else 'black'
        cell.detail_text_label.text = task.get('notes', '')
        cell.detail_text_label.text_color = '#888'
        cell.accessory_type = 'detail_button'
        return cell

    def tableview_can_delete(self, tableview, section, row):
        return True

    def tableview_delete(self, tableview, section, row):
        self.store.delete(self.rows[row]['id'])
        self.reload()

    # --- TableView delegate -----------------------------------------------
    def tableview_did_select(self, tableview, section, row):
        self.store.toggle(self.rows[row]['id'])
        self.reload()

    def tableview_accessory_button_tapped(self, tableview, section, row):
        self.edit_task(self.rows[row])


def main():
    store = TaskStore()
    root = TaskListView(store)
    nav = ui.NavigationView(root)
    nav.tint_color = ACCENT
    nav.present('fullscreen', hide_title_bar=False)


if __name__ == '__main__':
    main()
