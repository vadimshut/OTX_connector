from pulses_indicators.pulse import Pulse
from pulses_indicators.indicator import Indicator
from sender.sender_fid import ResultFid
import sqlite3
from configure import Configure
from database.database import Db


def clear():
    config_file = "configures/config.cfg"
    configure = Configure(config_file)
    db_path = configure.get_attribute('main', 'db_path')
    db_name = configure.get_attribute('main', 'db_name')
    db = Db(db_path, db_name)
    db.clear_table("Pulses")
    db.clear_table("Indicators")


def parse_pulses_list_and_write_to_db(db, pulses_list):
    for pulse in pulses_list:
        # Создание объекта класса Pulse
        pulse_instance = Pulse(pulse)
        pulse_instance.add_pulse_to_pulses_list(db.pulses_list)
        indicators = pulse_instance.get_all_indicators()
        for indicator in indicators:
            # Создание объекта класса Indicator
            indicator_instance = Indicator(indicator, pulse_instance.get_id_pulse())
            indicator_instance.add_indicator_to_indicators_list(db.indicators_list)
        # Записываем данные в БД, с обработкой ошибок в случае невозможности добавления данных в таблицы.
    try:
        db.write_all_pulses_to_the_pulses_table()
        db.write_all_indicators_to_the_indicator_table()
    except sqlite3.IntegrityError:
        print(f"Ошибка при добавлении: Pulse, Indicator:")  # Fix this string.


def syslog_sender(conf, list_of_data):
    # Создаем список данных для отправки в СИЕМ.
    # count - счетчик количества индикаторов отправленных в сием
    count = 0
    # В цикле проходим по списку и отправляем каждый IOC по UDP на СИЕМ.
    print("Start sending data...")
    for data in list_of_data:
        fid = ResultFid(data, conf)
        fid.syslog()
        count += 1
    print("Sending data completed successfully.")
    print(f"Всего отправлено IOC: {count}\n")