from pywinauto import Application

app = Application(backend='uia').connect(path="C:\\Users\\Dmitry\\AppData\\Local\\VtopeBot\\vtopebot.exe")

#b = app.Pane.child_window(title="Добавить аккаунт", control_type="Button").click()
s = app.Pane.print_control_identifiers(depth=100)

s =2