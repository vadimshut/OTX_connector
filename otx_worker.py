from OTXv2 import OTXv2
import requests
from datetime import datetime, timedelta
import time


# start_data = "01-09-2020"
class OtxWorker:
    def __init__(self, configure):
        self.__config = configure
        self.__otx = self.__get_otx_instance()

    def __get_otx_instance(self):
        api_key = self.__config.get_attribute('main', 'api_key')
        return OTXv2(api_key)

    def get_all_pulses_list(self):
        try:
            print("Start building pulses list...")
            pulses = self.__otx.getall()
            print("Request completed!")
            time.sleep(1)
            self.__config.set_attribute('main', 'old_revision_db', datetime.now().strftime('%Y%m%d'))
            self.__config.set_attribute('main', 'last_revision_db', datetime.now().strftime('%Y%m%d'))
            return pulses
        except requests.exceptions.ConnectionError:
            print("ConnectionError Отсутствует соединение с интернетом. Устраните неисправность!!! ")

    def get_new_pulses_list(self):

        def get_update_date():
            time_now = datetime.now()

            delta = timedelta(
                weeks=int(self.__config.get_attribute('timedelta', 'weeks')),
                days=int(self.__config.get_attribute('timedelta', 'days')),
                hours=int(self.__config.get_attribute('timedelta', 'hours')),
                minutes=int(self.__config.get_attribute('timedelta', 'minutes')),
                seconds=int(self.__config.get_attribute('timedelta', 'seconds')),
                milliseconds=int(self.__config.get_attribute('timedelta', 'milliseconds')),
                microseconds=int(self.__config.get_attribute('timedelta', 'microseconds')),
            )

            time_difference = (time_now - delta).strftime('%d-%m-%Y')
            print(f"Дата начала последнего обновления: {time_difference}")
            self.__config.set_attribute('main', 'old_revision_db',
                                        self.__config.get_attribute('main', 'last_revision_db'))
            self.__config.set_attribute('main', 'last_revision_db', time_now.strftime('%Y%m%d'))
            self.__config.set_attribute('timedelta', 'last_updating_date', time_difference)
            return time_difference

        list_of_new_pulses = self.__otx.getsince(get_update_date())
        print(f"Получено новое обновление. Доступно IOC: {len(list_of_new_pulses)}")
        return list_of_new_pulses