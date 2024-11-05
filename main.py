
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Treeview, Scrollbar
from tkinter import messagebox
import pathlib
import datetime
import tkinter as tk
import sqlite3
import datetime
from datetime import datetime, timedelta
import logging
import time
from selenium import webdriver

import hashlib
import random
from config import *
from loading import *
import csv
import logging
import os

logging.basicConfig(
    level=logging.DEBUG, filename = "mylog.txt",
    format = '%(asctime)s - %(levelname)s - %(module)s -  %(funcName)s: %(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    # раскомментировать, если нужны логи кириллицей в pycharm
    #encoding = 'utf-8',
    )

class MainWindow:

    def __init__(self, master):

        self.master = master
        self.master.geometry("1350x750+0+0")
        self.master.config(bg="grey37")

        f = Frame(self.master, height=1080, width=1920, bg="grey15", relief="ridge", bd=30)
        f.propagate(0)
        f.pack()

        self.mainTitle = Label(f, text="ШЕРЛОК", fg="orange1" ,bg="grey15", font=("Lusida Console", 30,)).place(relx=.5, y=100, anchor="center")
        self.down = Button(f, text="Загрузить данные", width=15, height=2, fg="grey91", bg="grey37",
                           font=("Helvetica", 12, "normal roman"), command=self.с_down)
        self.down.place(relx=.5, y=210, anchor="center")
        #self.down.place(x=480, y=210)


        self.scheme = Button(f, text="Схемы", width=15, height=2, fg="grey91", bg="grey37",
                           font=("Helvetica", 12, "normal roman"), command=self.с_scheme)
        self.scheme.place(relx=.5, y=310, anchor="center")
        self.scheme['state'] = 'disabled'


        self.orient = Button(f, text="Ориентировки", width=15, height=2, fg="grey91", bg="grey37",
                           font=("Helvetica", 12, "normal roman"), command=self.table)
        self.orient.place(relx=.5, y=410, anchor="center")
        self.orient['state'] = 'disabled'


        self.out = Button(f, text="Выйти", width=15, height=2, fg="grey91", bg="grey37",
                                  font=("Helvetica", 12, "normal roman"), command=self.c_out)
        self.out.place(relx=.5, y=510, anchor="center")



    def с_down(self):
        # Если скачивание было недавно, то данные с сайта не загружаем.
        # Используем ранее полученную информацию.

        if path_data.exists():
            print("файл существует")
            file = open("down_data.txt", 'r')
            data_list = file.read()
            file.close()
            # получаем дату-время последней загрузки в нужном формате
            date_down = datetime.datetime.strptime(data_list, '%Y-%m-%d %H:%M:%S')
            # получаем текущую дату-время в нужном формате
            data_now = datetime.datetime.now()
            # разница в минутах и округление
            diff = (data_now - date_down).total_seconds() / delta
            print(int(diff))
            if diff >= 1:
                #loading_auto()

                logging.debug('данные загружены')
                conn = sqlite3.connect("AUTODATA.db")
                logging.debug('соединение с бд')
                # создаём курсор для виртуального управления базой данных
                cur = conn.cursor()
                # удаляем таблицу со старыми данными
                cur.execute("DROP TABLE IF EXISTS AUTO")
                # создаем новую
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS AUTO (id INTEGER PRIMARY KEY, num_auto TEXT, data TEXT, camera TEXT, make_car TEXT, model_car TEXT)")
                logging.debug('создана таблица CREATE AUTO')
                # разбиваем список адресов на отдельные адреса

                for p in path:
                    # открываем файл по каждому адресу
                    file = open(p, 'r')
                    # преобразуем файл в список
                    data_list = [row for row in csv.reader(file)]
                    # заполняем таблицу по индексам
                    for data in data_list:
                        cur.execute("INSERT INTO AUTO VALUES (NULL,?,?,?,?,?)",
                                    (data[1], data[6], data[14], data[17], data[18],))
                    file.close()
                logging.debug('вставлены данные с открытого файла')

                # создаем таблицу исключения легковых тс
                cur.execute("CREATE TABLE IF NOT EXISTS CAR_MAKE (make_car TEXT)")
                cur.executemany("INSERT INTO CAR_MAKE VALUES(?);", car_make)

                cur.execute("CREATE TABLE IF NOT EXISTS CAR_MODEL (make_car TEXT, model_car TEXT)")
                cur.executemany("INSERT INTO CAR_MODEL VALUES(?,?);", car_model)

                cur.execute(
                    "CREATE TABLE IF NOT EXISTS ORIENT (id INTEGER PRIMARY KEY, row_num INTEGER, num_auto TEXT, data TEXT, info TEXT)")
                logging.debug('созданы остальные таблицы')
                conn.commit()
                # вставляем данные из orient.txt в таблицу ORIENT
                file = open("C:/Users/User/Проекты/Шерлок/orient.txt", 'r')
                logging.debug('открыт файл orient.txt')

                print(file)

                #conn = sqlite3.connect("AUTODATA.db")
                #cur = conn.cursor()
                for f in file:
                    cur.execute("INSERT INTO ORIENT VALUES (NULL,?,?,?,?)",
                                (f[0], f[1], f[2], f[3],))
                logging.debug('данные вставлены из файла orient.txt в таблицу ORIENT')
                conn.commit()
                conn.close()
                file.close()

                file = open("down_data.txt", 'w+')
                print("дата загрузки изменена")
                data_down = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                file.write(data_down)
                file.close()

                # по факту успешной загрузки показываем окно
                self.newWindow = Toplevel(self.master)
                self.newWindow.resizable(0, 0)

                self.app = InfoWindow(self.newWindow)
                self.newWindow.after(2000, self.newWindow.destroy)
                self.down['state'] = 'disabled'
                self.scheme['state'] = 'normal'
                self.orient['state'] = 'normal'
                # удаляем файл после переноса данных
                #os.remove(path_del)


                # удаляем файлы загрузки
                # загружаем данные с сайта в файлы загрузки
                # очищаем AUTO,заполняем ее данными
            else:
                print('работа без загрузки')
                logging.debug('работа без загрузки')

                self.newWindow = Toplevel(self.master)
                self.newWindow.resizable(0, 0)
                # self.app = Register(self.newWindow)
                self.app = InfoWindow2(self.newWindow)
                self.newWindow.after(2000, self.newWindow.destroy)
                self.down['state'] = 'disabled'
                self.scheme['state'] = 'normal'
                self.orient['state'] = 'normal'

                # вставляем данные из orient.txt в таблицу ORIENT
                file = open("C:/Users/User/Проекты/Шерлок/orient.txt", 'r')
                logging.debug('открыт файл orient.txt')


                conn = sqlite3.connect("AUTODATA.db")
                cur = conn.cursor()
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS ORIENT (id INTEGER PRIMARY KEY, row_num INTEGER, num_auto TEXT, data TEXT, info TEXT)")
                logging.debug('создана таблица ORIENT')
                for f in file:
                    cur.execute("INSERT INTO ORIENT VALUES (NULL,?,?,?,?)",
                                (f[0], f[1], f[2], f[3],))
                    print(f)
                logging.debug('данные вставлены из файла orient.txt в таблицу ORIENT')
                conn.commit()
                conn.close()
                file.close()

                # используем имеющиеся таблицы БД

        else:
            # загружаем данные с сайта в файлы загрузки
            # создаем AUTO,заполняем ее данными
            # создаем таблицы и заполняем их данными

            #loading_auto()

            logging.debug('данные загружены')
            conn = sqlite3.connect("AUTODATA.db")
            logging.debug('соединение с бд')
            # создаём курсор для виртуального управления базой данных
            cur = conn.cursor()
            # удаляем таблицу со старыми данными
            #cur.execute("DROP TABLE IF EXISTS AUTO")
            # создаем новую
            cur.execute(
                "CREATE TABLE IF NOT EXISTS AUTO (id INTEGER PRIMARY KEY, num_auto TEXT, data TEXT, camera TEXT, make_car TEXT, model_car TEXT)")
            logging.debug('создана таблица AUTO')
            # разбиваем список адресов на отдельные адреса

            for p in path:
                # открываем файл по каждому адресу
                file = open(p, 'r')
                # преобразуем файл в список
                data_list = [row for row in csv.reader(file)]
                # заполняем таблицу по индексам
                for data in data_list:
                    cur.execute("INSERT INTO AUTO VALUES (NULL,?,?,?,?,?)",
                                (data[1], data[6], data[14], data[17], data[18],))
            logging.debug('вставлены данные с открытого файла')
            # создаем таблицу исключения легковых тс
            cur.execute("CREATE TABLE IF NOT EXISTS CAR_MAKE (make_car TEXT)")
            cur.executemany("INSERT INTO CAR_MAKE VALUES(?);", car_make)

            cur.execute("CREATE TABLE IF NOT EXISTS CAR_MODEL (make_car TEXT, model_car TEXT)")
            cur.executemany("INSERT INTO CAR_MODEL VALUES(?,?);", car_model)

            cur.execute(
                "CREATE TABLE IF NOT EXISTS ORIENT (id INTEGER PRIMARY KEY, row_num INTEGER, num_auto TEXT, data TEXT, info TEXT)")
            logging.debug('созданы остальные таблицы')

            conn.commit()
            conn.close()
            file.close()

            file = open("down_data.txt", 'w+')
            print("файл создан")
            data_down = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file.write(data_down)
            file.close()

            # по факту успешной загрузки показываем окно
            self.newWindow = Toplevel(self.master)
            self.newWindow.resizable(0, 0)
            # self.app = Register(self.newWindow)
            self.app = InfoWindow(self.newWindow)
            self.newWindow.after(2000, self.newWindow.destroy)
            self.down['state'] = 'disabled'
            self.scheme['state'] = 'normal'
            self.orient['state'] = 'normal'
            # удаляем файл после переноса данных
            os.remove(path_del)



    def с_scheme(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.resizable(0, 0)
        self.app = Scheme(self.newWindow)

    def table(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.resizable(0, 0)
        self.app = Table(self.newWindow)

    def c_out(self):

        file = open("C:/Users/User/Проекты/Шерлок/orient.txt", 'w+')
        logging.debug('создан или открыт файл orient.txt')

        self.conn = sqlite3.connect("AUTODATA.db")
        self.cur = self.conn.cursor()
        self.cur.execute("select row_num , num_auto, data ,info from ORIENT ")
        rows = self.cur.fetchall()


        for row in rows:


            row = str(row)
            file.write(row)

        logging.debug('данные записаны из таблицы ORIENT в файл orient.txt')
        self.cur.execute("DROP TABLE IF EXISTS ORIENT")
        logging.debug('таблица ORIENT удалена')

        self.conn.close()

        file.close()
        root.destroy()

class InfoWindow:
    def __init__(self, master):
        self.master = master
        self.master.geometry("500x150+0+0")
        self.master.config(bg="grey80")
        f1 = Frame(self.master, height=1080, width=1920, bg="grey80", relief="ridge", bd=10)
        f1.propagate(0)
        f1.pack()
        self.mainTitle = Label(f1, text="Данные успешно загружены", fg="grey15" ,bg="grey80", font=("Helvetica", 20, "normal roman")).place(
            x=50, y=45)

class InfoWindow1:
    def __init__(self, master):
        self.master = master
        self.master.geometry("500x150+0+0")
        self.master.config(bg="grey80")

        f11 = Frame(self.master, height=1080, width=1920, bg="grey80", relief="ridge", bd=10)
        f11.propagate(0)
        f11.pack()
        self.mainTitle = Label(f11, text="Пароль неверный!", fg="grey15" ,bg="grey80", font=("Helvetica", 20, "normal roman")).place(
            x=110, y=45)

class InfoWindow2:

    def __init__(self, master):
        self.master = master
        self.master.geometry("500x150+0+0")
        self.master.config(bg="grey80")
        f12 = Frame(self.master, height=1080, width=1920, bg="grey80", relief="ridge", bd=10)
        f12.propagate(0)
        f12.pack()
        self.mainTitle = Label(f12, text="Работа без загрузки", fg="grey15" ,bg="grey80", font=("Helvetica", 20, "normal roman")).place(
            x=50, y=45)

class Scheme:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1350x750+0+0")
        self.master.config(bg="azure")
        f2 = Frame(self.master, height=1080, width=1920, bg="grey15", relief="ridge", bd=20)
        f2.propagate(0)
        f2.pack()

        self.mainTitle = Label(f2, text="Схемы незаконного перемещения товаров", bg="grey15", fg="grey79",
                               font=("Helvetica", 15, "normal roman")).place(relx=.5, y=20, anchor="center")

        self.label1 = Label(f2, justify=LEFT, text=" Для просмотра описания схем \n введите пароль:", fg="grey79", bg="grey15", font=("Helvetica", 12, "normal roman"))
        self.e_password1 = Entry(f2, width=5, font=("Helvetica", 10, "normal roman"))

        self.password1 = Button(f2, text="Применить", width=15, height=2, fg="grey91", bg="grey37",
                              font=("Helvetica", 12, "normal roman"), command=self.password1)
        self.scheme1 = Button(f2, text="Схема 1", width=15, height=2, fg="grey91", bg="grey37",
                              font=("Helvetica", 12, "normal roman"), command=self.c_scheme1)
        self.scheme2 = Button(f2, text="Схема 2", width=15, height=2, fg="grey91", bg="grey37",
                              font=("Helvetica", 12, "normal roman"), command=self.c_scheme2)
        self.scheme3 = Button(f2, text="Схема 3", width=15, height=2, fg="grey91", bg="grey37",
                              font=("Helvetica", 12, "normal roman"), command=self.c_scheme2)
        self.scheme4 = Button(f2, text="Схема 4", width=15, height=2, fg="grey91", bg="grey37",
                              font=("Helvetica", 12, "normal roman"), command=self.c_scheme4)
        self.scheme5 = Button(f2, text="Схема 5", width=15, height=2, fg="grey91", bg="grey37",
                              font=("Helvetica", 12, "normal roman"), command=self.c_scheme5)
        self.scheme6 = Button(f2, text="Схема 6", width=15, height=2, fg="grey91", bg="grey37",
                              font=("Helvetica", 12, "normal roman"), command=self.c_scheme6)

        self.cancel = Button(f2, text="Назад", width=15, height=2, fg="grey91", bg="grey37",
                             font=("Helvetica", 12, "normal roman"), command=self.c_cancel)

        self.label1.place(x=50, y=80)
        self.e_password1.place(x=190, y=101)
        self.password1.place(x=55, y=130)

        self.scheme1.place(x=55, y=300)
        self.scheme2.place(x=265, y=300)
        self.scheme3.place(x=475, y=300)
        self.scheme4.place(x=685, y=300)
        self.scheme5.place(x=895, y=300)
        self.scheme6.place(x=1105, y=300)
        self.cancel.place(x=55, y=610)

    def password1(self):
        if self.e_password1.get() == password:
            self.newWindow = Toplevel(self.master)
            self.newWindow.resizable(0, 0)
            self.app = SchemeDescription(self.newWindow)
            self.e_password1.delete(0, 'end')
        else:
            self.newWindow = Toplevel(self.master)
            self.newWindow.resizable(0, 0)
            # self.app = Register(self.newWindow)
            self.app = InfoWindow1(self.newWindow)
            self.newWindow.after(1000, self.newWindow.destroy)
            # очищаем поле ввода
            self.e_password1.delete(0, 'end')

    def c_scheme1(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.resizable(0, 0)
        self.app = Scheme1(self.newWindow)

    def c_scheme2(self):
        self.newWindow = Toplevel(self.master)
        self.newWindow.resizable(0, 0)
        self.app = Scheme2(self.newWindow)
    def c_scheme3(self):
        pass
    def c_scheme4(self):
        pass
    def c_scheme5(self):
        pass
    def c_scheme6(self):
        pass
    def c_cancel(self):
        self.master.destroy()

class Table:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1350x750+0+0")
        self.master.config(bg="grey15")
        f4 = Frame(self.master, height=1080, width=1920, bg="grey15", relief="ridge", bd=20)
        f4.propagate(0)
        f4.pack()

        self.mainTitle = Label(f4, text="Ориентировки", bg="grey15", fg="grey79",
                               font=("Helvetica", 16, "normal roman")).place(x=570, y=30)
        # дополнение на 20.10.24
        self.number1 = Label(f4, text="Номер АТС", fg="grey79", bg="grey15",
                             font=("Helvetica", 12, "normal roman"))
        self.number2 = Label(f4, text="(латинские буквы для всех ", fg="grey79", bg="grey15",
                             font=("Helvetica", 12, "normal roman"))
        self.number3 = Label(f4, text="номеров, кроме российских): ", fg="grey79", bg="grey15",
                              font=("Helvetica", 12, "normal roman"))
        self.info1 = Label(f4, text="Дополнительная", fg="grey79", bg="grey15",
                           font=("Helvetica", 12, "normal roman"))
        self.info2 = Label(f4, text="информация: ", fg="grey79", bg="grey15",
                           font=("Helvetica", 12, "normal roman"))
        self.e_number = Entry(f4, width=10, font=("Helvetica", 12, "normal roman"))
        self.e_info = Entry(f4, width=102, font=("Helvetica", 12, "normal roman"))

        self.number1.place(x=85, y=460)
        self.number2.place(x=85, y=480)
        self.number3.place(x=85, y=500)


        self.info1.place(x=85, y=540)
        self.info2.place(x=85, y=560)

        self.e_number.place(x=305, y=500)
        self.e_info.place(x=305, y=560)



        # создание элементов для ввода слов и значений
        self.tree = ttk.Treeview(f4, show="headings", height=13, columns=('#1', '#2', '#3', '#4'))
        self.tree.delete(*self.tree.get_children())

        self.tree.heading('#1', text='№', anchor='w')
        self.tree.heading('#2', text='Номер АТС', anchor='w')
        self.tree.heading('#3', text='Дата внесения', anchor='w')
        self.tree.heading('#4', text='Дополнительная информация', anchor='w')
        self.tree.place(x=85, y=82)

        self.tree.column("#1", stretch=NO, width=50)
        self.tree.column("#2", stretch=NO, width=100)
        self.tree.column("#3", stretch=NO, width=200)
        self.tree.column("#4", stretch=NO, width=776)



        style = ttk.Style()
        # для работы fieldbackground добавим
        style.theme_use("clam")

        style.configure("Treeview", font=("Helvetica", 12), fieldbackground="grey15", background="grey15",
                        foreground="grey79", rowheight=25)
        # style.configure("Treeview.Cell", foreground="grey79", borderwidth=1, relief="sunken")
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"), background="grey15", foreground="grey79",
                        relief="flat", borderwidth=1)
        style.configure('black.TSeparator', background="grey79")

        # рисуем таблицу
        ttk.Separator(master=self.tree, orient=HORIZONTAL, style='black.TSeparator', class_=ttk.Separator, takefocus=0,
                      cursor='plus'
                      ).place(x=0, y=25, relwidth=1)
        ttk.Separator(master=self.tree, orient=VERTICAL, style='black.TSeparator', class_=ttk.Separator, takefocus=0,
                      cursor='plus'
                      ).place(x=50, y=0, relheight=1)
        ttk.Separator(master=self.tree, orient=VERTICAL, style='black.TSeparator', class_=ttk.Separator, takefocus=0,
                      cursor='plus'
                      ).place(x=150, y=0, relheight=1)
        ttk.Separator(master=self.tree, orient=VERTICAL, style='black.TSeparator', class_=ttk.Separator, takefocus=0,
                      cursor='plus'
                      ).place(x=350, y=0, relheight=1)


        self.update = Button(f4, text="Изменить", width=15, height=2, fg="grey91", bg="grey37",
                             font=("Helvetica", 12, "normal roman"), command=self.c_update)

        self.delete = Button(f4, text="Удалить", width=15, height=2, fg="grey91", bg="grey37",
                             font=("Helvetica", 12, "normal roman"), command=self.c_delete)


        self.cancel = Button(f4, text="Назад", width=15, height=2, fg="grey91", bg="grey37",
                             font=("Helvetica", 12, "normal roman"), command=self.c_cancel)

        self.save = Button(f4, text="Сохранить", width=15, height=2, fg="grey91", bg="grey37",
                           font=("Helvetica", 12, "normal roman"), command=self.c_save)
        self.save.place(x=482, y=620)
        self.update.place(x=682, y=620)
        self.delete.place(x=882, y=620)
        self.cancel.place(x=1082, y=620)

        treeYScroll = ttk.Scrollbar(f4, orient=VERTICAL)
        treeYScroll.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=treeYScroll.set)
        treeYScroll.place(x=1215, y=82, height=358)

        self.conn = sqlite3.connect("AUTODATA.db")
        self.cur = self.conn.cursor()

        self.cur.execute("select row_num , num_auto, data ,info from ORIENT ")
        rows = self.cur.fetchall()
        for row in rows:
            self.tree.insert(parent='', index='end', values=(row[0], row[1], row[2], row[3]))

        self.conn.close()

    def c_update(self):
        self.all_items = self.tree.get_children()
        num_all_items = enumerate(self.all_items, start=1)
        spisok = list(num_all_items)
        # получаем номер выбранной строки
        selected_item = self.tree.focus()
        for n in spisok:
            if n[1] == selected_item:
                num_selected_item = n[0]
                self.conn = sqlite3.connect("AUTODATA.db")
                self.cur = self.conn.cursor()
                quere = f"""SELECT row_num, num_auto, info from ORIENT WHERE row_num={num_selected_item}"""
                self.cur.execute(quere)
                self.rows = self.cur.fetchone()

                self.e_number.insert(0, self.rows[1])
                self.e_info.insert(0, self.rows[2])
                self.conn.commit()

                self.cur.close()
                self.conn.close()


    def c_delete(self):
        #создаем нумерацию имеющихся строк
        self.all_items = self.tree.get_children()
        num_all_items = enumerate(self.all_items,start=1)
        spisok = list(num_all_items)

        # получаем номер выбранной строки

        selected_item = self.tree.focus()

        for n in spisok:
            if n[1]==selected_item:
                num_selected_item = n[0]
                self.conn = sqlite3.connect("AUTODATA.db")
                self.cur = self.conn.cursor()
                # удаляем данные
                self.cur.execute("DELETE FROM ORIENT WHERE row_num=?", (num_selected_item,))
                self.conn.commit()
                # обновляем порядковый номер
                self.cur.execute(
                    "UPDATE ORIENT SET row_num = (SELECT COUNT(*) FROM ORIENT AS ORIENT2 WHERE ORIENT2.rowid <= ORIENT.rowid )")
                self.conn.commit()
                # выводим обновленные данные
                self.tree.delete(*self.tree.get_children())
                self.cur.execute("select row_num , num_auto, data ,info from ORIENT ")
                rows = self.cur.fetchall()
                for row in rows:
                    self.tree.insert(parent='', index='end', values=(row[0], row[1], row[2], row[3]))
                self.cur.close()
                self.conn.close()

    def c_save(self):

        # условие на заполненность поля ввода номера
        if len(self.e_number.get()) > 0:
            self.conn = sqlite3.connect("AUTODATA.db")
            self.cur = self.conn.cursor()

            #создаем нумерацию имеющихся строк
            self.all_items = self.tree.get_children()
            num_all_items = enumerate(self.all_items, start=1)
            spisok = list(num_all_items)

            # получаем номер выбранной строки

            selected_item = self.tree.focus()

            for n in spisok:
                if n[1] == selected_item:
                    num_selected_item = n[0]
                    #self.conn = sqlite3.connect("AUTODATA.db")
                    #self.cur = self.conn.cursor()
                    # удаляем данные
                    self.cur.execute("DELETE FROM ORIENT WHERE row_num=?", (num_selected_item,))
                    self.conn.commit()


            # получаем данные из полей ввода
            # вставляем их в таблицу

            self.cur.execute("INSERT INTO ORIENT VALUES (NULL,NULL,?,NULL,?)",(self.e_number.get(), self.e_info.get(),))
            self.conn.commit()

            self.cur.execute(
                "UPDATE ORIENT SET row_num = (SELECT COUNT(*) FROM ORIENT AS ORIENT2 WHERE ORIENT2.rowid <= ORIENT.rowid)")
            self.conn.commit()

            self.cur.execute(
                "UPDATE ORIENT SET data = strftime('%Y-%m-%d %H:%M:%S')  WHERE row_num  = (SELECT MAX(o1.row_num) FROM ORIENT o1) ")
            self.conn.commit()

            self.cur.execute("select row_num , num_auto, data ,info from ORIENT ")

            self.tree.delete(*self.tree.get_children())
            rows = self.cur.fetchall()
            for row in rows:
                self.tree.insert(parent='', index='end', values=(row[0], row[1], row[2], row[3]))

            self.cur.close()
            self.conn.close()
            # очищаем поля ввода
            self.e_number.delete(0, 'end')
            self.e_info.delete(0, 'end')

    def c_cancel(self):
        self.master.destroy()

class SchemeDescription:

    def __init__(self, master):
        self.master = master
        self.master.geometry("1350x750+0+0")
        self.master.config(bg="azure")
        f5 = Frame(self.master, height=1080, width=1920, bg="grey15", relief="ridge", bd=20)
        f5.propagate(0)
        f5.pack()

        self.mainTitle = Label(f5, text="Описание схем незаконного перемещения товаров:", bg="grey15", fg="grey79",font=("Helvetica", 16, "normal roman")).place(relx=.5, y=20, anchor="center")
        self.d_scheme1 = Label(f5, text=d_scheme1, fg="grey79", bg="grey15", font=("Helvetica", 12, "normal roman"))
        self.d_scheme2 = Label(f5, text=d_scheme2, fg="grey79", bg="grey15", font=("Helvetica", 12, "normal roman"))
        self.d_scheme3 = Label(f5, text=d_scheme3, fg="grey79", bg="grey15", font=("Helvetica", 12, "normal roman"))
        self.d_scheme4 = Label(f5, text=d_scheme4, fg="grey79", bg="grey15", font=("Helvetica", 12, "normal roman"))
        self.d_scheme5 = Label(f5, text=d_scheme5, fg="grey79", bg="grey15", font=("Helvetica", 12, "normal roman"))
        self.d_scheme6 = Label(f5, text=d_scheme6, fg="grey79", bg="grey15", font=("Helvetica", 12, "normal roman"))
        self.cancel = Button(f5, text="Назад", width=15, height=2, fg="grey91", bg="grey37",
                             font=("Helvetica", 12, "normal roman"), command=self.c_cancel)

        self.d_scheme1.place(x=50, y=50)
        self.d_scheme2.place(x=50, y=140)
        self.d_scheme3.place(x=50, y=230)
        self.d_scheme4.place(x=50, y=320)
        self.d_scheme5.place(x=50, y=400)
        self.d_scheme6.place(x=50, y=490)
        self.cancel.place(x=50, y=610)

    def c_cancel(self):
        self.master.destroy()


class Scheme1:
    def __init__(self, master):

        self.master = master
        self.master.geometry("1535x790+0+0")
        self.master.config(bg="grey15")
        f6 = Frame(self.master, height=1080, width=1920, bg="grey15", relief="ridge", bd=20)
        f6.propagate(0)
        f6.pack()

        self.mainTitle = Label(f6, text="Схема 1", bg="grey15", fg="grey79", font=("Helvetica", 16, "normal roman")).place(relx=.5, y=20, anchor="center")

        # создание элементов для ввода слов и значений
        self.tree = ttk.Treeview(f6, show="headings", height=20, columns=('#1', '#2', '#3', '#4', '#5', '#6', '#7'))
        self.tree.heading('#1', text='№', anchor='w')
        self.tree.heading('#2', text='Номер АТС', anchor='w')
        self.tree.heading('#3', text='Дата и время', anchor='w')
        self.tree.heading('#4', text='Камера', anchor='w')
        self.tree.heading('#5', text='Марка', anchor='w')
        self.tree.heading('#6', text='Модель', anchor='w')
        self.tree.heading('#7', text='Ориентировка', anchor='w')
        self.tree.place(x=300, y=72)

        self.tree.column("#1", stretch=NO, width=70)
        self.tree.column("#2", stretch=NO, width=120)
        self.tree.column("#3", stretch=NO, width=190)
        self.tree.column("#4", stretch=NO, width=220)
        self.tree.column("#5", stretch=NO, width=130)
        self.tree.column("#6", stretch=NO, width=120)
        self.tree.column("#7", stretch=NO, width=300)

        treeYScroll = ttk.Scrollbar(f6, orient=VERTICAL)
        treeYScroll.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=treeYScroll.set)
        treeYScroll.place(x=1454, y=72, height=533)
        # treeYScroll.pack(side=RIGHT, fill=Y)

        style = ttk.Style()
        # для работы fieldbackground добавим
        style.theme_use("clam")
        style.configure("Treeview", font=("Helvetica", 12), fieldbackground="grey15", background="grey15", foreground="grey79", rowheight=25)
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"), background="grey15", foreground="grey79", relief="flat", borderwidth=1)
        style.configure('black.TSeparator', background="grey79")

        # рисуем таблицу
        ttk.Separator(master=self.tree, orient=HORIZONTAL, style='black.TSeparator', class_=ttk.Separator, takefocus=0, cursor='plus'
        ).place(x=0, y=25, relwidth=1)
        ttk.Separator(master=self.tree, orient=VERTICAL, style='black.TSeparator', class_=ttk.Separator, takefocus=0, cursor='plus'
        ).place(x=70, y=0, relheight=1)
        ttk.Separator(master=self.tree, orient=VERTICAL, style='black.TSeparator', class_=ttk.Separator, takefocus=0, cursor='plus'
        ).place(x=190, y=0, relheight=1)
        ttk.Separator(master=self.tree, orient=VERTICAL, style='black.TSeparator', class_=ttk.Separator, takefocus=0, cursor='plus'
        ).place(x=380, y=0, relheight=1)
        ttk.Separator(master=self.tree, orient=VERTICAL, style='black.TSeparator', class_=ttk.Separator, takefocus=0, cursor='plus'
        ).place(x=600, y=0, relheight=1)
        ttk.Separator(master=self.tree, orient=VERTICAL, style='black.TSeparator', class_=ttk.Separator, takefocus=0, cursor='plus'
        ).place(x=730, y=0, relheight=1)
        ttk.Separator(master=self.tree, orient=VERTICAL, style='black.TSeparator', class_=ttk.Separator, takefocus=0, cursor='plus'
        ).place(x=850, y=0, relheight=1)

        self.checkbut1 = Label(f6, text="Исключить легковые транспортные ", bg="grey15", fg="grey79",
                               font=("Helvetica", 12, "normal roman")).place(x=30, y=70)
        self.checkbut2 = Label(f6, text="средства:", bg="grey15", fg="grey79",
                               font=("Helvetica", 12, "normal roman")).place(x=30, y=95)
        self.checkbut3 = Label(f6, text="Вывести только грузовые ", bg="grey15", fg="grey79",
                               font=("Helvetica", 12, "normal roman")).place(x=30, y=170)
        self.checkbut4 = Label(f6, text="транспортные средства:", bg="grey15", fg="grey79",
                               font=("Helvetica", 12, "normal roman")).place(x=30, y=195)
        self.checkbut5 = Label(f6, text="с номерами РБ: ", bg="grey15", fg="grey79",
                               font=("Helvetica", 12, "normal roman")).place(x=30, y=220)

        # подключаем флажки
        self.enabled1 = IntVar()
        self.enabled2 = IntVar()
        self.enabled_checkbutton1 = Checkbutton(f6, variable = self.enabled1, bg="gray", height=1, width=1,fg="blue", onvalue = 1,offvalue = 0, command=self.checkbutton_changed)
        self.enabled_checkbutton2 = Checkbutton(f6, variable = self.enabled2, bg="gray", height=1, width=1,fg="blue", onvalue = 1,offvalue = 0, command=self.checkbutton_changed)
        self.cancel = Button(f6, text="Назад", width=15, height=2, fg="grey91", bg="grey37",
                             font=("Helvetica", 12, "normal roman"), command=self.c_cancel)

        self.enabled_checkbutton1.place(x=180, y=95)
        self.enabled_checkbutton2.place(x=180, y=220)
        self.cancel.place(x=1325, y=620)

        self.enabled_checkbutton1.select()
        self.enabled_checkbutton2.deselect()

        self.checkbutton_changed()
    def connect(self):
        self.tree.delete(*self.tree.get_children())
        self.conn = sqlite3.connect("AUTODATA.db")
        self.cur = self.conn.cursor()

    def close(self):
        rows = self.cur.fetchall()
        for row in rows:
            self.tree.insert(parent='', index='end', values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def checkbutton_changed(self):
        if self.enabled1.get() ==1 and self.enabled2.get() ==0:
            self.connect()
            self.cur.execute(scheme1_1_0)
            self.close()
        elif self.enabled1.get() ==0 and self.enabled2.get() ==0:
            self.connect()
            self.cur.execute(scheme1_0_0)
            self.close()
        elif self.enabled1.get() == 0 and self.enabled2.get() == 1:
            self.connect()
            self.cur.execute(scheme1_0_1)
            self.close()
        else:
            self.connect()
            self.cur.execute(scheme1_1_1)
            self.close()

    def c_cancel(self):
        self.master.destroy()

class Scheme2:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1350x750+0+0")
        # self.master.title("Online Quiz - Registration")
        self.master.config(bg="grey15")
        f6 = Frame(self.master, height=1080, width=1920, bg="grey15", relief="ridge", bd=20)
        f6.propagate(0)
        f6.pack()
        self.conn = sqlite3.connect("AUTODATA.db")
        self.cur = self.conn.cursor()
        self.cur.execute("SELECT num_auto, data, camera, make_car, model_car FROM AUTO WHERE make_car = 'Ford'")
        rows = self.cur.fetchall()
        for row in rows:
            self.tree.insert(parent='', index='end', values=(row[0], row[1], row[2], row[3], row[4]))

        self.conn.close()


root = Tk()
root.resizable(0, 0)
RegObj = MainWindow(root)
#root.wm_attributes ( '-alpha' , 0.5 ) # Полностью прозрачный
root.mainloop()