import sys
import sqlite3
import traceback
from ui import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QMessageBox, QTableWidget
from PyQt5.QtCore import QDate, QTime, Qt


class Dialog1(QDialog, Ui_Dialog1):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Ведите данные')

        self.memory = ''

        self.pushButton.clicked.connect(self.add_task)

    def set_params(self, date, type):
        self.date = date
        self.dateTimeEdit.setDate(QDate().fromString(date, 'dd-MM-yyyy'))
        if type == 'a':  # english!!!
            self.dateTimeEdit.setDisabled(True)
            self.type = 'a'  # english!!!
        elif type == 'o':  # english!!!
            self.dateTimeEdit.setEnabled(True)
            self.type = 'o'  # english!!!

    def add_task(self):
        a1, a2, a3 = self.plainTextEdit.toPlainText(), self.timeEdit.text(), self.timeEdit_2.text()

        if a1 == '':
            self.label_5.setText('Отсутствует название задачи')
        elif a2 > a3:
            self.label_5.setText('"С" не может быть больше "ПО"')
        else:
            con = sqlite3.connect('db.sqlite')
            cur = con.cursor()
            cur.execute("INSERT INTO tasks(date, task, frm, too, status, type) VALUES(?, ?, ?, ?, '-', ?)",
                        (self.date, a1, a2, a3, self.type))
            if self.type == 'a':  # english!!!
                cur.execute("INSERT INTO always_tasks(task, frm, too) VALUES(?, ?, ?)", (a1, a2, a3))
            con.commit()

            self.label_5.setText('Успешно выполненно')
            con.close()
            self.close()


class Dialog2(QDialog, Ui_Dialog2):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.con = sqlite3.connect('db.sqlite')
        self.cur = self.con.cursor()

        self.update_table()
        self.tableWidget.setEditTriggers(self.tableWidget.NoEditTriggers)

        self.tableWidget.cellDoubleClicked.connect(self.change_a_task)
        self.pushButton.clicked.connect(self.delete_a_task)

    def set_params(self, date):
        self.date = date

    def update_table(self):
        res = self.cur.execute("SELECT * FROM always_tasks")

        self.tableWidget.setRowCount(0)
        for i1, row in enumerate(res):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for i2, elem in enumerate(row):
                self.tableWidget.setItem(i1, i2, QTableWidgetItem(str(elem)))

    def delete_a_task(self):
        a = [i.row() for i in self.tableWidget.selectedItems()]
        if a != []:
            value = QMessageBox.question(self, '', "Действительно удалить №" + ', '.join([str(i + 1) for i in a]),
                                         QMessageBox.Yes, QMessageBox.No)
            if value == QMessageBox.Yes:
                for i in range(len(a)):
                    i1 = self.tableWidget.item(a[i], 0).text()
                    self.work_with_tasks(i1)
                    a[i] = i1

                self.cur.execute("DELETE FROM always_tasks WHERE id IN (" + ', '.join(a) + ')')
                self.con.commit()
                self.update_table()

    def work_with_tasks(self, ID):
        task = next(self.cur.execute("SELECT * FROM always_tasks WHERE id = " + ID))
        if self.radioButton_2.isChecked():
            self.cur.execute("""DELETE FROM tasks
                WHERE (date = ?) AND (task = ?) AND (frm = ?) AND (too = ?) and (type = 'a')""",
                             (self.date, task[1], task[2], task[3]))
        elif self.radioButton_3.isChecked():
            self.cur.execute("""DELETE FROM tasks
                WHERE (task = ?) AND (frm = ?) AND (too = ?) and (type = 'a')""",
                             (task[1], task[2], task[3]))

    def change_a_task(self, y, x):
        if x == 1:
            a = Name_Dialog(self)
            a.set_val(self.tableWidget.item(y, x).text(), self.tableWidget.item(y, 0).text(),
                      self.date)
            a.exec()
            self.update_table()
        elif x == 2 or x == 3:
            a = Time_Dialog(self)
            a.set_val(self.tableWidget.item(y, x).text(), 'frm' if x == 2 else 'too',
                      self.tableWidget.item(y, 0).text(), self.date)
            a.exec()
            self.update_table()

    def keyPressEvent(self, event):
        key = event.key()
        modif = int(event.modifiers())
        if key == Qt.Key_Delete:
            self.delete_a_task()

class Name_Dialog(QDialog, Ui_Name_Dialog):
    def __init__(self, par):
        super().__init__()
        self.par = par
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.value = ''

        self.pushButton.clicked.connect(self.change)
        self.pushButton_2.clicked.connect(self.close)

    def set_val(self, value, id, date, t_type='a'):
        self.t_type = t_type
        self.value = value
        self.date = date
        self.id = id
        self.plainTextEdit.setPlainText(value)

    def change(self):
        self.con = sqlite3.connect('db.sqlite')
        self.cur = self.con.cursor()
        if self.t_type == 'a':  # english
            res = [i for i in self.cur.execute("SELECT * from always_tasks WHERE id = ?", (int(self.id),))]
            self.work_with_tasks(res[0][2], res[0][3])
            self.cur.execute("""UPDATE always_tasks SET task = ? WHERE id = ?""",
                             (self.plainTextEdit.toPlainText().replace('\n', ' '), self.id))
        elif self.t_type == 'o':  # english
            self.cur.execute("UPDATE tasks SET task = ? WHERE id = ?", (self.plainTextEdit.toPlainText(), self.id))

        self.con.commit()
        self.con.close()
        self.close()

    def work_with_tasks(self, frm, too):
        if self.par.radioButton_2.isChecked():
            self.cur.execute("""UPDATE tasks
                             SET task = ? WHERE task = ? AND frm = ? AND too = ? AND date = ?""",
                             (self.plainTextEdit.toPlainText(), self.value, frm, too, self.date))

        elif self.par.radioButton_3.isChecked():
            self.cur.execute("""UPDATE tasks
                             SET task = ? WHERE task = ? AND frm = ? AND too = ?""",
                             (self.plainTextEdit.toPlainText(), self.value, frm, too))


class Time_Dialog(QDialog, Ui_Time_Dialog):
    def __init__(self, par):
        super().__init__()
        self.par = par
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.value = '00:00'
        self.column = 'frm'

        self.pushButton.clicked.connect(self.change_a)
        self.pushButton_2.clicked.connect(self.close)

    def set_val(self, value, column, id, date, t_type='a'):
        self.t_type = t_type
        self.value = value
        self.column = column
        self.id = id
        self.date = date
        self.timeEdit.setTime(QTime().fromString(value.rjust(5, '0'), 'hh:mm'))

    def change_a(self):
        self.con = sqlite3.connect('db.sqlite')
        self.cur = self.con.cursor()
        if self.t_type == 'a':  # english
            res = [i for i in self.cur.execute("SELECT * from always_tasks WHERE id = ?", (int(self.id),))]
            self.work_with_tasks(res[0][1], res[0][2], res[0][3])
            self.cur.execute("UPDATE always_tasks SET " + self.column +
                             " = ? WHERE id = ?", (self.timeEdit.text(), self.id))
        elif self.t_type == 'o':  # english
            self.cur.execute("UPDATE tasks SET " + self.column + " = ? WHERE id = ?",
                             (self.timeEdit.text(), self.id))

        self.con.commit()
        self.con.close()
        self.close()

    def work_with_tasks(self, task, frm, too):
        if self.par.radioButton_2.isChecked():
            self.cur.execute(f"""UPDATE tasks
                             SET {self.column} = ? WHERE task = ? AND frm = ? AND too = ? AND date = ?""",
                             (self.timeEdit.text(), task, frm, too, self.date))

        elif self.par.radioButton_3.isChecked():
            self.cur.execute(f"""UPDATE tasks
                             SET {self.column} = ? WHERE task = ? AND frm = ? AND too = ?""",
                             (self.timeEdit.text(), task, frm, too))


class Tip_Name_Dialog(QDialog, Ui_Tip_Name_Dialog):
    def __init__(self, par):
        super().__init__()
        self.par = par
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.pushButton.clicked.connect(self.create_tip)
        self.pushButton_2.clicked.connect(self.close)

    def create_tip(self):
        if self.lineEdit.text() != '':
            self.par.file = self.lineEdit.text() + '.txt'
            self.close()
            self.par.compl = True