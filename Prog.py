# -*- coding: utf-8 -*-
import sys
import csv
import sqlite3 as db
import os

#зададим значения переменных по-умолчанию
sqlite_db = "my.db"
csv_file = "Sacramentorealestatetransactions.csv"
result_path = "result" #слэш в конце не ставить

#считаем параметры коммандной строки
if len(sys.argv) > 1:
    if sys.argv[1].endswith(".csv"):
	    csv_file = sys.argv[1]
    else:
        print("Неверно указан *.csv файл (первый параметр)\nВыбран файл по-умолчанию (Sacramentorealestatetransactions.csv)")
    if len(sys.argv) > 2:
        result_path = sys.argv[2]
		
#Подключение к базе
conn = db.connect(sqlite_db)
#Создание курсора
c = conn.cursor()

#создадим таблицу records в SQLite если её нет
c.execute("""
    CREATE TABLE IF NOT EXISTS records (
      street TEXT,
      city TEXT,
      zip INTEGER,
      state TEXT,
      beds INTEGER,
      baths INTEGER,
      sq__ft INTEGER,
      type TEXT,
      sale_date TEXT,
      price INTEGER,
      latitude REAL,
      longitude REAL)
""")
conn.commit()

#Функция занесения записи в базу (параметром является добавляемая строка)
def add_rec(row):
    c.execute("""INSERT INTO records (
      street,
      city,
      zip,
      state,
      beds,
      baths,
      sq__ft,
      type,
      sale_date,
      price,
      latitude,
      longitude)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",row)
    #Подтверждение отправки данных в базу
    conn.commit()

#функция создания таблицы с информацией сгруппированной по городу(city) или zip-коду
def create_table(col_name,result_path,param):
    c2 = conn.cursor()
    substr = ""
    #в зависимости от выберем нужный запрос
    if (col_name == "city"):
        c2.execute("SELECT * FROM records WHERE city='%s'" % str(param) )
    else:
        c2.execute("SELECT * FROM records WHERE zip=%d" % int(param) )
    row = c2.fetchone()
    while row is not None:
        substr += "<tr>"
        for i in row:
            substr += "<th>%s</th>" % (i)
        substr += "</tr>"
        row = c2.fetchone()
    #формирование кода страницы с таблицей
    table = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test</title>
        <meta charset = "utf-8">
    </head>
    <body>
        <table border="1">
            <caption>%s</caption>
            <tr>
                <th>street</th>
                <th>city</th>
                <th>zip</th>
                <th>state</th>
                <th>beds</th>
                <th>baths</th>
                <th>sq__ft</th>
                <th>type</th>
                <th>sale_date</th>
                <th>price</th>
                <th>latitude</th>
                <th>longitude</th>
            </tr>
            %s
        </table>
    </body>
    </html>""" % (str(param),str(substr))
    #запись сформированного файла на диск в указанную директорию
    f = open("%s/%s" % (str(result_path),str(param).replace(" ","_")), 'w')
    f.write(str(table))
    f.close()
    #Завершение соединения
    c2.close()
    
#Создадим папку для таблиц
try: #if os.path.exists(result_path):
    os.makedirs(result_path)
except OSError:
    pass

#Считывание файла csv и добавление полученных данных в БД SQLite
with open(csv_file, "rU") as f:
    reader = csv.reader(f)
    next(reader) #Возможно вместо этого надо использовать csv.DictReader??
    for row in reader:
        add_rec(row)

#Запрашиваем из базы список уникальных Городов(city)
c.execute("SELECT DISTINCT city FROM records ORDER BY city")
row = c.fetchone()

#Сформируем гипперсылки на таблицы с информацией по городам
substr1 = ""
while row is not None:
    substr1 += "<a href=\%s/%s/%s>%s</a>, " % (os.path.abspath(os.curdir),result_path,str(row)[3:-3].replace(" ","_"),str(row)[3:-3]) #использовал срез т.к. иначе выводит в виде (u'CITY',)   :(
    #заодно тут же создадим таблицу по данному городу
    create_table("city",result_path,str(row)[3:-3])
    row = c.fetchone()

#Запрашиваем из базы список уникальных Zip-кодов
c.execute("SELECT DISTINCT zip FROM records ORDER BY zip")
row = c.fetchone()

#Сформируем гипперсылки на таблицы с информацией по zip-кодам
substr2 = ""
while row is not None:
    substr2 += "<a href=\%s/%s/%s>%s</a>, " % (os.path.abspath(os.curdir),result_path,str(row)[1:-2],str(row)[1:-2]) #использовал срез т.к. иначе выводит в виде (95111,)   :(
    #заодно тут же создадим таблицу по данному zip-коду
    create_table("zip",result_path,str(row)[1:-2])
    row = c.fetchone()

#формирем страницу index
index = """
<!DOCTYPE html>
<html>
    <head>
        <title>Тестовое задание</title>
        <meta charset = "utf-8">
    </head>
    <body>
        <h1>Список городов</h1>
            <p>
                %s
            </p>
        <h1>Список Zip-кодов</h1>
            <p>
                %s
            </p>
    </body>
</html>
""" % (substr1,substr2)

#Записываем сформированный файл index на диск
f = open('index.html', 'w')
f.write(index)
f.close()

#Завершение соединения
c.close()
conn.close()




