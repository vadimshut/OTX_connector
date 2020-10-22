from otx_worker import OtxWorker
from functions import *
import time
import schedule


def run():
    # Получаем необходимые параметры из конфиг файла
    config_file = "configures/config.cfg"
    configure = Configure(config_file)
    first_start = configure.get_attribute('main', 'first_start')
    old_revision_db = int(configure.get_attribute('main', 'old_revision_db'))
    # clear_tables = configure.get_attribute('main', 'clear_tables')
    db_path = configure.get_attribute('main', 'db_path')
    db_name = configure.get_attribute('main', 'db_name')
    db = Db(db_path, db_name)
    otx = OtxWorker(configure)

    # Проверяем впервые ли запущен скрипт:
    # Если first_start==True качаем всю базу. Иначе проверяем только обновления
    if first_start == 'True':
        print("Программа запускается впервые. Идет процесс сзоздания и скачивания БД...")
        time.sleep(1)
        configure.set_attribute('main', 'first_start', 'False')
        # Создаем базу данных с 2-мя таблицами Pulses, Indicators
        db.create_table_pulses_and_indicators()
        # Получаем список IOC на которые подписан экземпляр класса OTX
        pulses_list = otx.get_all_pulses_list()
        parse_pulses_list_and_write_to_db(db, pulses_list)
        list_of_data = db.get_of_list_of_data_to_send_to_siem()
        syslog_sender(configure, list_of_data)
    else:
        print("Идет проверка наличия обновлений IOC...")
        # Получаем список новых пульсов
        new_pulses = otx.get_new_pulses_list()
        # Проверка на нличие новых пульсов в БД
        pulses_list, count_update, count_new = db.checked_pulse(new_pulses)
        if count_new != 0 and count_update != 0:
            parse_pulses_list_and_write_to_db(db, pulses_list)
            list_of_data = db.get_of_new_list_of_data_to_send_to_siem(old_revision_db)
            syslog_sender(configure, list_of_data)


if __name__ == '__main__':
    run()

    # schedule.every(2).minutes.do(run)
    # while True:
    #     schedule.run_pending()