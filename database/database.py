import sqlite3


def decorator(func):
    def wrapper(self):
        """checking_for_database_existence"""
        path = f"{self.__db_path}\\{self.__db_name}"
        try:
            sqlite3.connect(f'file:{path}?mode=ro', uri=True)
            ret = func()
            return ret
        except sqlite3.OperationalError:
            print('Database does not exist! Check the existence of the database!')

    return wrapper


class Db:
    def __init__(self, path, name):
        self.pulses_list = []
        self.indicators_list = []
        self.__db_path = path
        self.__db_name = name

    def create_table_pulses_and_indicators(self):
        create_tbl_pulses = '''
        CREATE TABLE Pulses (
                              id_pulse TEXT NOT NULL PRIMARY KEY,
                              author_name TEXT,
                              created TEXT,
                              modified TEXT,
                              name TEXT,
                              description TEXT,
                              reference TEXT,
                              tags TEXT,
                              malware_families TEXT,
                              attack_ids TEXT,
                              revision INTEGER,
                              revision_db INTEGER
                              );
        '''

        create_tbl_indicators = '''
        CREATE TABLE Indicators (
                       id_pulse TEXT NOT NULL,
                       id_indicator INTEGER NOT NULL,
                       created TEXT,
                       description TEXT,
                       indicator TEXT,
                       type TEXT,                      
                       CONSTRAINT id_pul_ind PRIMARY KEY (id_pulse, id_indicator),
                       FOREIGN KEY (id_pulse) REFERENCES Pulses(id_pulse) ON UPDATE CASCADE,
                       FOREIGN KEY (id_pulse) REFERENCES Pulses(id_pulse) ON DELETE CASCADE 
                       );
        '''
        conn = sqlite3.connect(f"{self.__db_path}\\{self.__db_name}")
        cursor = conn.cursor()
        cursor.execute(create_tbl_pulses)
        cursor.execute(create_tbl_indicators)
        cursor.execute("PRAGMA foreign_keys=1;")
        conn.commit()
        conn.close()

    def delete_table(self, table_name):
        delete_table_query = f"DROP TABLE {table_name}"
        conn = sqlite3.connect(f"{self.__db_path}\\{self.__db_name}")
        cursor = conn.cursor()
        cursor.execute(delete_table_query)
        conn.commit()
        conn.close()

    def clear_table(self, table_name):
        request_query = f"DELETE FROM {table_name};"
        conn = sqlite3.connect(f"{self.__db_path}\\{self.__db_name}")
        conn.execute("PRAGMA foreign_keys=1;")
        cursor = conn.cursor()
        cursor.execute(request_query)
        conn.commit()
        conn.close()

    def write_all_pulses_to_the_pulses_table(self):
        insert_query = f"INSERT INTO Pulses VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
        conn = sqlite3.connect(f"{self.__db_path}\\{self.__db_name}")
        cursor = conn.cursor()
        cursor.executemany(insert_query, self.pulses_list)
        conn.commit()
        conn.close()
        print(f"In Pulses table was added {len(self.pulses_list)} values")
        self.pulses_list.clear()

    def write_all_indicators_to_the_indicator_table(self):
        insert_query = f"INSERT INTO Indicators VALUES (?,?,?,?,?,?)"
        conn = sqlite3.connect(f"{self.__db_path}\\{self.__db_name}")
        cursor = conn.cursor()
        cursor.executemany(insert_query, self.indicators_list)
        conn.commit()
        conn.close()
        print(f"In Indicators table was added {len(self.indicators_list)} values")
        self.indicators_list.clear()

    def get_of_list_of_data_to_send_to_siem(self):
        request_query = """ 
            SELECT * 
            FROM Pulses LEFT JOIN Indicators
            ON Indicators.id_pulse=Pulses.id_pulse
            WHERE Indicators.id_pulse IS NOT null and Indicators.id_indicator IS NOT null;
        """
        conn = sqlite3.connect(f"{self.__db_path}\\{self.__db_name}")
        cursor = conn.cursor()
        cursor.execute(request_query)
        data = cursor.fetchall()
        conn.close()
        return data

    def get_of_new_list_of_data_to_send_to_siem(self, old_revision_db):
        request_query = f""" 
            SELECT * 
            FROM Pulses LEFT JOIN Indicators
            ON Indicators.id_pulse=Pulses.id_pulse
            WHERE Indicators.id_pulse IS NOT null 
            AND Indicators.id_indicator IS NOT null 
            AND Pulses.revision_db > {old_revision_db};
        """
        conn = sqlite3.connect(f"{self.__db_path}\\{self.__db_name}")
        cursor = conn.cursor()
        cursor.execute(request_query)
        data = cursor.fetchall()
        conn.close()
        return data

    def __get_id_pulses_list(self):
        request_query = f"SELECT id_pulse FROM Pulses;"
        conn = sqlite3.connect(f"{self.__db_path}\\{self.__db_name}")
        cursor = conn.cursor()
        cursor.execute(request_query)
        data = cursor.fetchall()
        data = [item for item_tuple in data for item in item_tuple]
        conn.close()
        return data

    def __delete_pulse(self, pulse_id):
        request_query = f"DELETE FROM Pulses WHERE id_pulse='{pulse_id}';"
        conn = sqlite3.connect(f"{self.__db_path}\\{self.__db_name}")
        conn.execute("PRAGMA foreign_keys=1;")
        cursor = conn.cursor()
        cursor.execute(request_query)
        conn.commit()
        conn.close()
        # print(f"Pulse: {pulse_id} is deleted from DB.")

    def __get_pulse_revision(self, id_pulse):
        request_query = f"SELECT revision FROM Pulses WHERE id_pulse='{id_pulse}';"
        conn = sqlite3.connect(f"{self.__db_path}\\{self.__db_name}")
        cursor = conn.cursor()
        cursor.execute(request_query)
        data = cursor.fetchall()
        data = [item for item_tuple in data for item in item_tuple]
        data = int(data[0]) if len(data) == 1 else data
        conn.close()
        return data

    def checked_pulse(self, new_pulses_list):
        count_update = 0
        count_new = 0
        new_list = []
        id_pulses_list = self.__get_id_pulses_list()

        for new_pulse in new_pulses_list:
            if new_pulse['id'] in id_pulses_list:
                old_rev = self.__get_pulse_revision(new_pulse['id'])
                if new_pulse['revision'] != old_rev:
                    print(f"Необходимо обновить пульc ID: {new_pulse['id']} "
                          f"OLD-Revision: {old_rev}, NEW-Revision: {new_pulse['revision']}")
                    self.__delete_pulse(new_pulse['id'])
                    new_list.append(new_pulse)
                    count_update += 1
                # else:
                #     print(f"IOC id:{new_pulse['id']} существует в БД. Revision: {new_pulse['revision']}")
            else:
                # print(f"IOC id:{new_pulse['id']} необходимо добавить в БД. ")
                new_list.append(new_pulse)
                count_new += 1
        print(f"В БД необходимо обновить {count_update}, добавить {count_new} пульсов")
        return new_list, count_update, count_new
