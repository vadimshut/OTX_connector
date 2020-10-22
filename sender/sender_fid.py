import socket


class ResultFid:

    @staticmethod
    def __get_formatted_date(date):
        """
            Преобразовать дату формата 2020-08-27T07:25:35
            в формат Jul 11 1992 04:30:35 MSK для отправки в СИЕМ
        """
        month_name = {
            1: 'Jan',
            2: 'Feb',
            3: 'Mar',
            4: 'Apr',
            6: 'Jun',
            5: 'May',
            7: 'Jul',
            8: 'Aug',
            9: 'Sep',
            10: 'Oct',
            11: 'Nov',
            12: 'Dec'
        }
        list_date_and_time = date.split('T')
        date_path = list_date_and_time[0].split('-')
        last_path = 'MSK'

        return f"{month_name[int(date_path[1])]} {date_path[2]} {date_path[0]} {list_date_and_time[1]} {last_path}"

    def __init__(self, data, configure):
        self.__config = configure
        self.__device_vendor = self.__config.get_attribute('fields', 'device_vendor')
        self.__device_product = data[1]                                                         # author_name
        self.__device_version = self.__config.get_attribute('fields', 'device_version')
        self.__device_event_class_id = data[10]                                                 #revision
        self.__name = data[4]                                                                   # name
        self.__severity = self.__config.get_attribute('fields', 'severity')
        self.__id_pulse = data[0]                                                               # id_pulse
        self.__created_pulse = self.__get_formatted_date(data[2])                               # created
        self.__modified_pulse = self.__get_formatted_date(data[3])                              # modified
        self.__description_pulse = data[5]                                                      # description
        self.__reference = data[6]                                                              # reference
        self.__tags = data[7]                                                                   # tags
        self.__malware_families = data[8]                                                       # malware_families
        self.__attack_ids = data[9]                                                             # attack_ids
        self.__id_indicator = data[13]                                                          # id_indicator
        self.__created_indicator = self.__get_formatted_date(data[14])                          # created
        self.__description_indicator = data[15]                                                 # description
        self.__indicator = data[16]                                                             # indicator
        self.__type_indicator = data[17]                                                        # type

    def create_data_in_cef_format(self):
        """Метод прнинимает трансформирует данные из БД в CEF формат"""
        cef = f"""
            CEF:0|{self.__device_vendor}|
            {self.__device_product}|
            {self.__device_version}|
            {self.__device_event_class_id}|
            {self.__name}|
            {self.__severity}|
            msg={self.__id_pulse} 
            fileCreateTime={self.__created_pulse} 
            fileModificationTime={self.__modified_pulse}
            cs1Label=pulse description cs1={self.__description_pulse} 
            request={self.__reference} 
            requestContext={self.__tags}
            cs2Label=malware families cs2={self.__malware_families} 
            cs3Label=attack ids cs3={self.__attack_ids}     
            deviceFacility={self.__id_indicator} 
            deviceCustomDate1Label=created indicator deviceCustomDate1={self.__created_indicator} 
            cs4Label=indicator description cs4={self.__description_indicator} 
            cs5Label=indicator value cs5={self.__indicator} 
            cs6Label=type of indicator cs6={self.__type_indicator}

            """

        return cef

    def syslog(self):
        """Метод отправляет единицу данных. В данном случае одну строчку из БД трансформированную в CEF формат"""
        host = self.__config.get_attribute('main', 'syslog_host')
        port = int(self.__config.get_attribute('main', 'syslog_port'))
        data = self.create_data_in_cef_format()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(data.encode(), (host, port))
        s.close()