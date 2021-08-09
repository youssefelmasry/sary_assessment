# Sary Task 

## How to start
* clone the project
* create a virtualenv
* setup and create postgresql db with these credentials:
	1. dbname: sarydb
	2. dbuser: saryuser
	3. dbpassword: sarypassword
* navigate to the main directory which `manage.py` lives
* install requirements `pip install -r requirements.txt`
* migrate database `python manage.py migrate`
* create admin user `python manage.py createsupseruser` 
* run up the server `python manage.py runserver`
* to run tests `python manage.py test`

*P.S*: 
- You can change Database credentials to whatever you want but make sure to change it in .env file
- The created dbuser should have `createdb` role in order to run the tests successfully
- The .env file must not be shared on git but this is for just demo

### APIs Documentation
After running up the server go to `http://localhost:8000/swagger/`

#### Sorting
User can sort reservations by reservation time by specifying query param `ordering` in the URL, and add `-` to the field you sort for to reverse the result
	
Example:
1. Ascending `api/restaurant/reservation/get_today_reservations/?ordering=reserve_start_time`
2. Descending `api/restaurant/reservation/get_today_reservations/?ordering=-reserve_start_time`

#### Filtering
User can filter reservation by table by specifying query param `table__table_number` in the URL. And also for a date range with query param `created`.
In date range you can specify an exact date or range by using for ex. `__gte`

Examples:
1. filter for table 5 `api/restaurant/reservation/get_all_reservations/?table__table_number=5`
2. filter for table 5 and 12 `api/restaurant/reservation/get_all_reservations/?table__table_number=5,12`
3. filter for a date range `api/restaurant/reservation/get_all_reservations/?created__gt=2021-08-01&created__lte=2021-08-09`


### DB tables:
	User:
		username: string
		employee_number: int(unique, max_digits=4)
		is_admin: boolean(default=False)
		password: string(min_char=6)

	Table:
		table_number: int(unique)
		table_number_of_seats: int

	Reservation:
		table: foreignkey(Table)
		reserve_start_time: time
		reserve_end_time: time
		created: date
