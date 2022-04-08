# import pandas
from datetime import datetime
from .database_connection import DatabaseConnection

DATE_FORMAT = "%Y-%m-%d"

query_dict = {
    101: [f'SELECT COUNT(*) FROM availability WHERE Date BETWEEN ? AND ? AND "101"=1',
          f'UPDATE availability SET "101" = 0 WHERE Date BETWEEN ? AND ?'],
    102: [f'SELECT COUNT(*) FROM availability WHERE Date BETWEEN ? AND ? AND "102"=1',
          f'UPDATE availability SET "102" = 0 WHERE Date BETWEEN ? AND ?'],
    103: [f'SELECT COUNT(*) FROM availability WHERE Date BETWEEN ? AND ? AND "103"=1',
          f'UPDATE availability SET "103" = 0 WHERE Date BETWEEN ? AND ?'],
    104: [f'SELECT COUNT(*) FROM availability WHERE Date BETWEEN ? AND ? AND "104"=1',
          f'UPDATE availability SET "104" = 0 WHERE Date BETWEEN ? AND ?'],
    105: [f'SELECT COUNT(*) FROM availability WHERE Date BETWEEN ? AND ? AND "105"=1',
          f'UPDATE availability SET "105" = 0 WHERE Date BETWEEN ? AND ?'],
    201: [f'SELECT COUNT(*) FROM availability WHERE Date BETWEEN ? AND ? AND "201"=1',
          f'UPDATE availability SET "201" = 0 WHERE Date BETWEEN ? AND ?'],
    202: [f'SELECT COUNT(*) FROM availability WHERE Date BETWEEN ? AND ? AND "202"=1',
          f'UPDATE availability SET "202" = 0 WHERE Date BETWEEN ? AND ?'],
    203: [f'SELECT COUNT(*) FROM availability WHERE Date BETWEEN ? AND ? AND "203"=1',
          f'UPDATE availability SET "203" = 0 WHERE Date BETWEEN ? AND ?'],
    204: [f'SELECT COUNT(*) FROM availability WHERE Date BETWEEN ? AND ? AND "204"=1',
          f'UPDATE availability SET "204" = 0 WHERE Date BETWEEN ? AND ?'],
    205: [f'SELECT COUNT(*) FROM availability WHERE Date BETWEEN ? AND ? AND "205"=1',
          f'UPDATE availability SET "205" = 0 WHERE Date BETWEEN ? AND ?']
}


def initialize() -> None:
    """
    Has multiple functionalities:
        1. When part 1 is uncommented and part 2 is commented, it uses the excel file to create a database, with two
        tables - rooms and availability. The availability table is a calendar table for the next 30 days.
        2. Once part 1 is run, it shall be commented and part 2 is run every time a booking occurs. Part 2 deletes
        the previous days entries and updates the calendar with more days, ensuring users can always book 30 days in
        advance.
    Note: Call this function every time to proceed with the booking.
    :return: None
    """

    """
        PART 1
    """

    # data_from_excel = pandas.read_excel(r'room_excel.xlsx', sheet_name='Sheet1')
    # dataframe = pandas.DataFrame(data_from_excel, columns=['Room Number', 'Category', 'Price'])
    #
    # with DatabaseConnection('data.db') as connection:
    #     cursor = connection.cursor()
    #     dataframe.to_sql('rooms', connection, if_exists='append', index=False)
    #
    # with DatabaseConnection('data.db') as connection:
    #     cursor = connection.cursor()
    #     cursor.execute('CREATE TABLE IF NOT EXISTS availability(Date TEXT PRIMARY KEY, "101" INTEGER, "102" INTEGER,'
    #                    ' "103" INTEGER, "104" INTEGER, "105" INTEGER, "201" INTEGER, "202" INTEGER, "203" INTEGER,'
    #                    ' "204" INTEGER, "205" INTEGER)')
    #     for data in cursor.execute("SELECT julianday('now')"):
    #         pass
    #     for date in cursor.execute('SELECT date(?)', data):
    #         pass
    #     data = (data[0],)
    #     for _ in range(30):
    #         cursor.execute('INSERT OR IGNORE INTO availability VALUES(?, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)', date)
    #         data = (data[0]+1,)
    #         for date in cursor.execute('SELECT date(?)', data):
    #             pass

    """
        PART 2   
    """

    with DatabaseConnection('data.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT julianday('now')")
        data = cursor.fetchone()
        cursor.execute('SELECT date(?)', data)
        date = cursor.fetchone()
        data = (data[0],)
        cursor.execute('SELECT date(?)', data)
        date = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) from availability where Date < ?', date)
        length_of_updation = cursor.fetchone()
        cursor.execute('DELETE FROM availability where Date < ?', date)

    with DatabaseConnection('data.db') as connection:
        cursor = connection.cursor()
        data = (data[0] + 30 - length_of_updation[0],)
        cursor.execute('SELECT date(?)', data)
        date = cursor.fetchone()
        for _ in range(length_of_updation[0]):
            cursor.execute('INSERT OR IGNORE INTO availability VALUES(?, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)', date)
            data = (data[0] + 1,)
            for date in cursor.execute('SELECT date(?)', data):
                pass


def display() -> None:
    """
    Displays two tables: rooms(the categories and prices) and availability(a calendar table showing availability).
    :return: None
    """
    with DatabaseConnection('data.db') as connection:
        cursor = connection.cursor()
        for room in cursor.execute('SELECT * FROM rooms'):
            print(room)

    with DatabaseConnection('data.db') as connection:
        cursor = connection.cursor()
        for available in cursor.execute('SELECT * from availability'):
            print(available)


def is_available(from_date=None, to_date=None, room_class=None) -> tuple[bool, str, str, tuple[int, int], int]:
    """
    Checks if a certain category has rooms available between two dates.
    :param from_date: The starting date of booking
    :param to_date: The ending date of booking
    :param room_class: The category of the room
    :return: tuple regarding the information and availability of room
    """
    with DatabaseConnection('data.db') as connection:
        cursor = connection.cursor()
        room_numbers = []
        for room in cursor.execute('SELECT "Room Number", Price FROM rooms WHERE Category=?', (room_class,)):
            room_numbers.append(room)

        a = datetime.strptime(from_date, DATE_FORMAT)
        b = datetime.strptime(to_date, DATE_FORMAT)
        delta = b - a
        difference_dates = delta.days + 1

        for room in room_numbers:
            cursor = connection.cursor()
            query = query_dict[room[0]][0]
            for data in cursor.execute(query, (from_date, to_date)):
                if data[0] == difference_dates:
                    return True, from_date, to_date, room, difference_dates
        else:
            return False, from_date, to_date, room, difference_dates


def book_a_room(from_date=None, to_date=None, room=None, difference_dates=None) -> tuple[int, float, int]:
    """
    Books a room using specified dates and updates its availability according to the parameters.
    :param from_date: The starting date of booking
    :param to_date: The ending date of booking
    :param room: The number and price of the room
    :param difference_dates: The number of days
    :return: None
    """
    with DatabaseConnection('data.db') as connection:
        cursor = connection.cursor()
        query = query_dict[room[0]][1]
        cursor.execute(query, (from_date, to_date))
        bill_amount = difference_dates * room[1]
        return room[0], bill_amount, difference_dates


def get_rooms() -> list[dict]:
    """
    Gets details of all the rooms from the database and converts it to a list of dictionaries.
    :return: rooms as list[dict]
    """
    with DatabaseConnection('data.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM rooms')
        rooms = [{'room_no': row[0], 'room_type': row[1], 'price': row[2]} for row in cursor.fetchall()]

        return rooms


def get_room_details() -> list[dict]:
    """
    Gets details of all the rooms and availability from the database and converts it to a list of dictionaries.
    :return: rooms as list[dict]
    """
    with DatabaseConnection('data.db') as connection:
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM availability')
        availability = [{'Date': row[0],
                         'Room-101': row[1], 'Room-102': row[2], 'Room-103': row[3], 'Room-104': row[4],
                         'Room-105': row[5],
                         'Room-201': row[6], 'Room-202': row[7], 'Room-203': row[8], 'Room-204': row[9],
                         'Room-205': row[10],
                         } for row in cursor.fetchall()]
        return availability
