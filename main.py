from pywinauto import Application
import time

app = Application(backend='uia').connect(path="C:\\Users\\Dmitry\\AppData\\Local\\VtopeBot\\vtopebot.exe")
app = app.Pane

button_add_account = app.child_window(title="Добавить аккаунт", control_type="Button")
button_add_account.click()

w = app.child_window(title="backgroundModalWidget", control_type="Custom")
w.wait('exists')

#s = app.print_control_identifiers(depth=100)

app['Edit2'].set_text('123')
app['Edit1'].set_text('1234')

app['Добавить аккаунт2'].click()

#w.wait_not('exists')

