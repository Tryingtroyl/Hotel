from flask import Flask, request, url_for, render_template, redirect
from utils import database

app = Flask(__name__)


@app.route('/')
def home():
    database.initialize()
    rooms = database.get_rooms()
    return render_template('home.html', rooms=rooms)


@app.route('/room/details')
def room_details():
    availability = database.get_room_details()
    return render_template('show_room_details.html', availability=availability)


@app.route('/room/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        date_from = request.form.get('date-from')
        date_to = request.form.get('date-to')
        room_type = request.form.get('room-type')
        booking_availability = database.is_available(date_from, date_to, room_type)
        if not booking_availability[0]:
            return render_template('booking.html', message="No Rooms Available for selected range and room category")
        else:
            bill = database.book_a_room(booking_availability[1], booking_availability[2], booking_availability[3],
                                        booking_availability[4])
            message = [f"Confirmed booking!",
                       f"Room Number: {bill[0]}",
                       f"Bill Amount: Rs. {bill[1]}",
                       f"Number of days: {bill[2]}",
                       f"Check-in date: {date_from}",
                       f"Check-out date: {date_to}"]
            return render_template('booking.html', message=message)
    return render_template('booking.html', message=[f"Check for room availability and book room"])


if __name__ == '__main__':
    app.run(debug=True)
