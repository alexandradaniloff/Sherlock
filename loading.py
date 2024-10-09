from tkinter import *
from tkinter import ttk
import logging
import time
from selenium import webdriver


logging.basicConfig(
    level=logging.INFO,

    format = "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    )

#logging.debug("Это сообщение DEBUG")
#logging.info("Это сообщение INFO")
#logging.warning("Это сообщение WARNING")
#logging.error("Это сообщение ERROR")
#logging.critical("Это сообщение CRITICAL")

# как пример, реализовано введение номера авто на сайте автокод с нажатием кнопки "Проверить авто",
# затем - скачивание договора купли-продажи с последующим его удалением из загрузок.

# адрес сайта с которого получаем выгрузку
url1 = "https://avtocod.ru/"
url2 = "https://avtocod.ru/dogovor-kupli-prodagi-ts"

# путь поля для ввода данных
input_xpath = "/html/body/div[3]/div[4]/div[1]/div/div/div/form/div/div[2]/div/div/input"

# значение, которое вводим в поле
data1 = "М475РУ67"

# путь кнопки выгрузки данных
chek_xpath1 ="/html/body/div[3]/div[4]/div[1]/div/div/div/form/div/div[2]/div/button"
chek_xpath2 = "/html/body/div[3]/div[4]/div/div/div/article/p[4]/strong/a"
load = "/html/body/div/div/div/div/div[1]/div[2]/div[2]/button[2]"

def loading_auto():
    driver = webdriver.Chrome()
    driver.get(url1)
    #driver.find_element(by="xpath", value=example_xpath).click()
    driver.find_element(by="xpath", value=input_xpath).send_keys(data1)
    driver.find_element(by="xpath", value=chek_xpath1).click()
    time.sleep(5)
    driver.get(url2)

    driver.find_element(by ="xpath", value=chek_xpath2).click()
    driver.find_element(by="xpath", value=load).click()
    time.sleep(10)

    # Закрытие текущей вкладки
    driver.close()

    # Закрытие всего браузера
    driver.quit()

