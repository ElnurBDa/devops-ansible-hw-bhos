from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import time
import mysql.connector
from mysql.connector import Error

print("App started!")

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class PCStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    brand = db.Column(db.String(50), nullable=False)

def wait_for_db():
    """Wait for the database to be available"""
    while True:
        try:
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            if connection.is_connected():
                print("Connected to the database.")
                connection.close()
                break
        except Error as e:
            print(f"Error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def initialize_db():
    """Create tables if they don't exist"""
    try:
        with app.app_context():
            db.create_all()
        print("Database tables created!")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Initialize DB and wait for MySQL to be available
wait_for_db()

# Initialize tables
initialize_db()

@app.route('/')
def index():
    products = PCStore.query.all()
    return render_template('index.html', products=products)

@app.route('/add', methods=['POST'])
def add_product():
    name = request.form['name']
    price = float(request.form['price'])
    brand = request.form['brand']
    new_product = PCStore(name=name, price=price, brand=brand)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_product(id):
    product = PCStore.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = PCStore.query.get(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.brand = request.form['brand']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', product=product)

if __name__ == "__main__":
    # Initialize DB before starting the app
    app.run(host="0.0.0.0", debug=True)
