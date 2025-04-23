from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from datetime import datetime
import json
import os

TASKS_FILE = "tasks.json"

class TaskManager(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        self.search_input = TextInput(hint_text="🔍 Search tasks", multiline=False, size_hint_y=None, height=40)
        self.search_input.bind(text=self.update_display)
        self.add_widget(self.search_input)

        self.status_filter = Spinner(text='All', values=['All', 'Done', 'Not Done'], size_hint_y=None, height=40)
        self.status_filter.bind(text=self.update_display)
        self.add_widget(self.status_filter)

        self.task_input = TextInput(hint_text="Task description", multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.task_input)

        self.priority_spinner = Spinner(text='Low', values=('Low', 'Medium', 'High'), size_hint_y=None, height=40)
        self.add_widget(self.priority_spinner)

        self.date_input = TextInput(hint_text="Due Date (YYYY-MM-DD)", multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.date_input)

        self.add_button = Button(text="Add Task", size_hint_y=None, height=40)
        self.add_button.bind(on_press=self.add_task)
        self.add_widget(self.add_button)

        self.task_list_container = ScrollView()
        self.task_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        self.task_list_container.add_widget(self.task_list)
        self.add_widget(self.task_list_container)

        self.tasks = []
        self.load_tasks()
        self.update_display()
        self.notify_due_today()

    def add_task(self, instance):
        task_text = self.task_input.text.strip()
        priority = self.priority_spinner.text
        due_date = self.date_input.text.strip()

        if not task_text:
            self.show_popup("Error", "Please enter a task description.")
            return

        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            self.show_popup("Invalid Date", "Please use YYYY-MM-DD format.")
            return

        task = {'task': task_text, 'priority': priority, 'due': due_date, 'done': False}
        self.tasks.append(task)
        self.task_input.text = ""
        self.date_input.text = ""
        self.save_tasks()
        self.update_display()

    def update_display(self, *args):
        query = self.search_input.text.lower()
        filter_status = self.status_filter.text

        self.task_list.clear_widgets()
        for i, task in enumerate(self.tasks):
            if query and query not in task['task'].lower():
                continue
            if filter_status == 'Done' and not task['done']:
                continue
            if filter_status == 'Not Done' and task['done']:
                continue

            text = f"{task['task']} | Due: {task['due']} | {task['priority']}"
            if task['done']:
                text += " ✔"

            task_label = Label(text=text, size_hint_y=None, height=40)
            done_button = Button(text="Undo" if task['done'] else "Mark Done", size_hint_y=None, height=30)
            done_button.bind(on_press=lambda inst, idx=i: self.toggle_done(idx))

            box = BoxLayout(size_hint_y=None, height=70)
            box.add_widget(task_label)
            box.add_widget(done_button)

            self.task_list.add_widget(box)

    def toggle_done(self, index):
        self.tasks[index]['done'] = not self.tasks[index]['done']
        self.save_tasks()
        self.update_display()

    def save_tasks(self):
        with open(TASKS_FILE, 'w') as f:
            json.dump(self.tasks, f)

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                self.tasks = json.load(f)

    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(300, 200))
        popup.open()

    def notify_due_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        due_today = [t for t in self.tasks if t['due'] == today and not t['done']]
        if due_today:
            message = "\n".join(f"- {t['task']} (Priority: {t['priority']})" for t in due_today)
            self.show_popup("📅 Due Today", message)

class TaskApp(App):
    def build(self):
        return TaskManager()

if __name__ == "__main__":
    TaskApp().run()
