from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Замените на свой секретный ключ

# SQLite database configuration
DATABASE_URL = 'sqlite:///shop.db'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Upload folder configuration
UPLOAD_FOLDER = 'static/images/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Admin credentials (в реальном проекте храните в безопасном месте)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# Models
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String(200), nullable=False)

# Create database tables
Base.metadata.create_all(bind=engine)

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Пожалуйста, войдите как администратор', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/catalog')
def catalog():
    db = next(get_db())
    try:
        products = db.query(Product).all()
        return render_template('catalog.html', products=products)
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return render_template('catalog.html', products=[])

@app.route('/product/<int:product_id>')
def product(product_id):
    db = next(get_db())
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return "Product not found", 404
        return render_template('product.html', product=product)
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return "Database error", 500

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        return render_template('contact.html', success=True)
    return render_template('contact.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash('Вы успешно вошли в систему', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin():
    db = next(get_db())
    products = db.query(Product).all()
    return render_template('admin.html', products=products)

@app.route('/admin/add_product', methods=['POST'])
@admin_required
def admin_add_product():
    if 'image' not in request.files:
        flash('Нет файла изображения', 'danger')
        return redirect(url_for('admin'))
    
    file = request.files['image']
    if file.filename == '':
        flash('Не выбран файл изображения', 'danger')
        return redirect(url_for('admin'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        db = next(get_db())
        try:
            new_product = Product(
                name=request.form['name'],
                description=request.form['description'],
                price=float(request.form['price']),
                image=f'/static/images/products/{filename}'
            )
            db.add(new_product)
            db.commit()
            flash('Товар успешно добавлен', 'success')
        except SQLAlchemyError as e:
            db.rollback()
            flash('Ошибка при добавлении товара', 'danger')
            print(f"Database error: {e}")
    else:
        flash('Недопустимый формат файла', 'danger')
    
    return redirect(url_for('admin'))

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    db = next(get_db())
    product = db.query(Product).get(product_id)
    
    if request.method == 'POST':
        try:
            product.name = request.form['name']
            product.description = request.form['description']
            product.price = float(request.form['price'])
            
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    product.image = f'/static/images/products/{filename}'
            
            db.commit()
            flash('Товар успешно обновлен', 'success')
            return redirect(url_for('admin'))
        except SQLAlchemyError as e:
            db.rollback()
            flash('Ошибка при обновлении товара', 'danger')
            print(f"Database error: {e}")
    
    return render_template('admin_edit.html', product=product)

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    db = next(get_db())
    try:
        product = db.query(Product).get(product_id)
        if product:
            # Удаление файла изображения
            image_path = os.path.join(app.root_path, product.image.lstrip('/'))
            if os.path.exists(image_path):
                os.remove(image_path)
            
            db.delete(product)
            db.commit()
            flash('Товар успешно удален', 'success')
        else:
            flash('Товар не найден', 'danger')
    except SQLAlchemyError as e:
        db.rollback()
        flash('Ошибка при удалении товара', 'danger')
        print(f"Database error: {e}")
    
    return redirect(url_for('admin'))

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        # В будущем здесь можно добавить обработку заказа
        # и сохранение его в базу данных
        return jsonify({'success': True})
    return render_template('order.html')

if __name__ == '__main__':
    app.run(debug=True) 