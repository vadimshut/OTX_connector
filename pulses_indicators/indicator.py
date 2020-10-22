class Indicator:
    def __init__(self, data, pulse_id):
        self.__id_pulse = pulse_id
        self.__id_indicator = data['id']
        self.__created_indicator = data['created']
        self.__description_indicator = data['description']
        self.__indicator = data['indicator']
        self.__type_indicator = data['type']

    def create(self):
        """
        Создает кортеж с информацией об индикаторе. Для безопасной записи в базу данных
        :return:  one_indicator
        """
        one_indicator = (
            self.__id_pulse,
            self.__id_indicator,
            self.__created_indicator,
            self.__description_indicator,
            self.__indicator,
            self.__type_indicator
        )

        return one_indicator

    def add_indicator_to_indicators_list(self, indicator_lists):
        """
            Метод добавляет кортеж индикатора (one_indicator) в список, для дальнейшей отправки в БД
        """
        indicator_lists.append(self.create())