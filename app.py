from flask import Flask, render_template, request, redirect, session, flash, url_for
import hashlib
import uuid

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# -------- Mock Data --------
mock_users = {}  # email: hashed_password
mock_bookings = []  # list of booking dicts

# -------- Helper Functions --------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_mock_email(email, booking_info):
    print(f"[MOCK EMAIL] Sent to {email}:\nBooking confirmed for {booking_info['movie']}\n"
          f"Seat: {booking_info['seat']}, Date: {booking_info['date']}, Time: {booking_info['time']}\n"
          f"Booking ID: {booking_info['id']}\n")

# -------- Routes --------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in mock_users:
            flash("Account already exists.")
            return redirect(url_for('login'))

        mock_users[email] = hash_password(password)
        flash("Account created! Please login.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed = hash_password(password)

        if email in mock_users and mock_users[email] == hashed:
            session['user'] = email
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password.")
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))

    movies = [
        {'title': 'The Grand Premiere', 'genre': 'Drama', 'poster': 'posters/movie1.jpg'},
        {'title': 'Laugh Riot', 'genre': 'Comedy', 'poster': 'posters/movie2.jpg'},
        {'title': 'Edge of Tomorrow', 'genre': 'Action', 'poster': 'posters/movie3.jpg'},
        {'title': 'Haunted Nights', 'genre': 'Horror', 'poster': 'posters/movie4.jpg'}
    ]
    return render_template('home.html', user=session['user'], movies=movies)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Temporarily store booking form in session
        session['pending_booking'] = {
            'movie': 'Example Movie',
            'seat': request.form['seat'],
            'date': request.form['date'],
            'time': request.form['time']
        }
        return redirect(url_for('payment'))

    return render_template('booking_form.html', movie='Example Movie')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user' not in session or 'pending_booking' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Pretend to process the fake payment
        booking_info = session['pending_booking']
        booking_info['user'] = session['user']
        booking_info['id'] = str(uuid.uuid4())[:8]

        mock_bookings.append(booking_info)
        session['last_booking'] = booking_info
        send_mock_email(session['user'], booking_info)
        session.pop('pending_booking', None)
        flash("Payment successful. Ticket booked!")

        return redirect(url_for('confirmation'))

    return render_template('payment.html')

@app.route('/confirmation')
def confirmation():
    if 'user' not in session or 'last_booking' not in session:
        return redirect(url_for('login'))

    booking = session['last_booking']
    return render_template('confirmation.html', booking=booking)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('index'))



# 🔍 Debug Route: View all mock bookings
@app.route('/debug/bookings')
def debug_bookings():
    if not mock_bookings:
        return "No bookings yet."

    html = "<h2>All Bookings</h2><ul>"
    for b in mock_bookings:
        html += f"<li><b>User:</b> {b['user']}, <b>Movie:</b> {b['movie']}, <b>Seat:</b> {b['seat']}, <b>Date:</b> {b['date']}, <b>Time:</b> {b['time']}, <b>ID:</b> {b['id']}</li>"
    html += "</ul>"
    return html

if __name__ == '__main__':
    print("🚀 Mock MovieMagic running at http://127.0.0.1:5000")
    app.run(debug=True)

