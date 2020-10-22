from datetime import datetime


class Pulse:
    def __init__(self, data):
        self.__pulse_id_pulse = data['id']
        self.__pulse_author_name = data['author_name']
        self.__pulse_created = data['created']
        self.__pulse_modified = data['modified']
        self.__pulse_name = data['name']
        self.__pulse_description = data['description']
        self.__pulse_reference = ', '.join(data['references'])
        self.__pulse_tags = ', '.join(data['tags'])
        self.__pulse_malware_families = ', '.join(data['malware_families'])
        self.__pulse_attack_ids = ', '.join(data['attack_ids'])
        self.__pulse_revision = data['revision']
        self.__indicators = data['indicators']
        self.__revision_db = int(datetime.now().strftime('%Y%m%d'))

    def __create(self):
        """
               Создает кортеж с информацией об пульсе. Для безопасной записи в базу данных
               :return:  one_pulse
        """
        one_pulse = (
            self.__pulse_id_pulse,
            self.__pulse_author_name,
            self.__pulse_created,
            self.__pulse_modified,
            self.__pulse_name,
            self.__pulse_description,
            self.__pulse_reference,
            self.__pulse_tags,
            self.__pulse_malware_families,
            self.__pulse_attack_ids,
            self.__pulse_revision,
            self.__revision_db
        )

        return one_pulse

    def add_pulse_to_pulses_list(self, pulses_list):
        """
            Метод добавляет кортеж пульса (one_pulse) в список, для дальнейшей отправки в БД
        """
        pulses_list.append(self.__create())

    def get_id_pulse(self):
        """Метод возвращает из БД список ID индикаторов"""
        return self.__pulse_id_pulse

    def get_all_indicators(self):
        """Метод возвращает список инфикаторов относящихся к экземпляру пульса"""
        return self.__indicators