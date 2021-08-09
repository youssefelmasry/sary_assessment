from datetime import date, datetime
from restaurant.models import Table, Reservation
from itertools import groupby
from django_filters import FilterSet

# Constants
RESTAURANT_OPEN_TIME = datetime.strptime("12:00", "%H:%M").time()
RESTAURANT_CLOSE_TIME = datetime.strptime("23:59", "%H:%M").time()

def group_by_value_list_of_dict(list_dict):
    keyfunc = lambda d: next(iter(d.values()))
    return {k: [y for d in g for y in d] for k, g in groupby(sorted(list_dict, key=keyfunc), key=keyfunc)}

def check_if_slots_available(reserve_start_time, reserve_end_time, table_number):
    '''
    1. get list of reservations of table_number order_by start_time
    2. if table has no reservations return true
    3. check if start_time >= open_time and start_time >= last_reservation.end_time
        and end_time <= first_reservation.start_time and end_time <= close_time
    '''

    if reserve_start_time < reserve_end_time and \
        reserve_start_time >= RESTAURANT_OPEN_TIME and \
        reserve_start_time >= datetime.now().time() and \
        reserve_end_time <= RESTAURANT_CLOSE_TIME:

        table_reservations = Reservation.objects.filter(table__table_number=table_number, 
                                                        created=datetime.today().date(), 
                                                        reserve_end_time__gte=datetime.now().time()
                                                        ).order_by('reserve_start_time')
        if not table_reservations:
            return True
    
        for table in table_reservations:
            if table.reserve_start_time <= reserve_start_time <= table.reserve_end_time \
                or table.reserve_start_time <= reserve_end_time <= table.reserve_end_time:
                return False
        return True
    
    return False

def check_table_availability(table_number):
    table_reservations = list(Reservation.objects.filter(table__table_number=table_number, 
                                                    created=datetime.today().date(), 
                                                    reserve_end_time__gte=datetime.now().time()
                                                    ).order_by('reserve_start_time'))

    # if table has no reservations
    if not table_reservations:
        to_end_of_day = f"{str(datetime.now().time())[:5]} - {str(RESTAURANT_CLOSE_TIME)[:5]}"
        return [{to_end_of_day: table_number}]
    
    available_tables = []

    # check if there is (17 mins) between now and the next first reservation start time => only for the first reservation
    if (datetime.combine(date.today(), table_reservations[0].reserve_start_time) - datetime.now()).total_seconds() >= 1020:
        available_tables.append({f"{str(datetime.now().time())[:5]} - {str(table_reservations[0].reserve_start_time)[:5]}": table_number})


    # for last reservation
    if table_reservations[-1].reserve_end_time < RESTAURANT_CLOSE_TIME:
        available_tables.append({f"{str(table_reservations[-1].reserve_end_time)[:5]} - 23:59": table_number})
    
    # add reserved tables available time slots
    len_reserved_tables = len(table_reservations[:-1])
    for index in range(len_reserved_tables):
        end_time = table_reservations[index].reserve_end_time
        next_start_time = table_reservations[index+1].reserve_start_time
        
        if end_time != next_start_time:
            available_tables.append({f"{str(end_time)[:5]} - {str(next_start_time)[:5]}": table_number})
    
    return available_tables

def get_minimum_number_of_seats(required_seats, tables):
    for table in tables:
        if required_seats <= table.table_number_of_seats:
            return Table.objects.filter(table_number_of_seats=table.table_number_of_seats)


def get_table_with_minimum_number_of_seats(required_seats):
    tables = Table.objects.order_by("table_number_of_seats")

    available_tables = []
    
    # check if required seats in range of our available tables seats number
    if not tables.first().table_number_of_seats <= required_seats <= tables.last().table_number_of_seats:
        return (False, "Required Seats Out of Limits")
    
    minimum_seats_tables = get_minimum_number_of_seats(required_seats, tables)
    for table in minimum_seats_tables:
        # check on all tables with the same matching table's number of seats
        available_tables.extend(check_table_availability(table.table_number))

    if not available_tables:
        return (False, "No Available Seats")

    return (True, group_by_value_list_of_dict(available_tables))

def is_table_has_reservations(table):
    return Reservation.objects.filter(created=date.today(), table=table, reserve_start_time__gte=datetime.now().time()).exists()
