from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Category, Ad
from forms import RegistrationForm, LoginForm, AdForm, SearchForm
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classified_ads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Initialize database and create default categories
def init_db():
    """Initialize database tables and create default categories"""
    db.create_all()
    
    # Create default categories if they don't exist
    if Category.query.count() == 0:
        categories = [
            Category(name='Electronics', description='Electronics and gadgets'),
            Category(name='Vehicles', description='Cars, motorcycles, and other vehicles'),
            Category(name='Real Estate', description='Houses, apartments, and land'),
            Category(name='Furniture', description='Home and office furniture'),
            Category(name='Clothing', description='Clothes and accessories'),
            Category(name='Books', description='Books and magazines'),
            Category(name='Sports', description='Sports equipment and gear'),
            Category(name='Services', description='Professional services'),
            Category(name='Other', description='Other items')
        ]
        for category in categories:
            db.session.add(category)
        db.session.commit()


# Initialize database on app startup
with app.app_context():
    init_db()


@app.route('/')
def index():
    """Home page showing recent ads"""
    page = request.args.get('page', 1, type=int)
    ads = Ad.query.filter_by(is_active=True).order_by(Ad.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    categories = Category.query.all()
    return render_template('index.html', ads=ads, categories=categories)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match!', 'error')
            return render_template('register.html', form=form)
        
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/create_ad', methods=['GET', 'POST'])
@login_required
def create_ad():
    """Create a new classified ad"""
    form = AdForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        ad = Ad(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            location=form.location.data,
            contact_info=form.contact_info.data,
            category_id=form.category_id.data,
            user_id=current_user.id
        )
        db.session.add(ad)
        db.session.commit()
        flash('Ad created successfully!', 'success')
        return redirect(url_for('ad_detail', ad_id=ad.id))
    
    return render_template('create_ad.html', form=form)


@app.route('/ad/<int:ad_id>')
def ad_detail(ad_id):
    """View ad details"""
    ad = Ad.query.get_or_404(ad_id)
    return render_template('ad_detail.html', ad=ad)


@app.route('/edit_ad/<int:ad_id>', methods=['GET', 'POST'])
@login_required
def edit_ad(ad_id):
    """Edit an existing ad"""
    ad = Ad.query.get_or_404(ad_id)
    
    # Check if user owns the ad
    if ad.user_id != current_user.id:
        flash('You do not have permission to edit this ad.', 'error')
        return redirect(url_for('ad_detail', ad_id=ad_id))
    
    form = AdForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        ad.title = form.title.data
        ad.description = form.description.data
        ad.price = form.price.data
        ad.location = form.location.data
        ad.contact_info = form.contact_info.data
        ad.category_id = form.category_id.data
        ad.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Ad updated successfully!', 'success')
        return redirect(url_for('ad_detail', ad_id=ad.id))
    
    # Pre-fill form with existing data
    form.title.data = ad.title
    form.description.data = ad.description
    form.price.data = ad.price
    form.location.data = ad.location
    form.contact_info.data = ad.contact_info
    form.category_id.data = ad.category_id
    
    return render_template('create_ad.html', form=form, ad=ad, is_edit=True)


@app.route('/delete_ad/<int:ad_id>', methods=['POST'])
@login_required
def delete_ad(ad_id):
    """Delete an ad"""
    ad = Ad.query.get_or_404(ad_id)
    
    # Check if user owns the ad
    if ad.user_id != current_user.id:
        flash('You do not have permission to delete this ad.', 'error')
        return redirect(url_for('ad_detail', ad_id=ad_id))
    
    db.session.delete(ad)
    db.session.commit()
    flash('Ad deleted successfully!', 'success')
    return redirect(url_for('my_ads'))


@app.route('/my_ads')
@login_required
def my_ads():
    """View user's own ads"""
    ads = Ad.query.filter_by(user_id=current_user.id).order_by(Ad.created_at.desc()).all()
    return render_template('my_ads.html', ads=ads)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search and filter ads"""
    form = SearchForm()
    form.category_id.choices = [(0, 'All Categories')] + [(c.id, c.name) for c in Category.query.all()]
    
    ads = Ad.query.filter_by(is_active=True)
    
    if form.validate_on_submit() or request.method == 'GET':
        query = request.args.get('query', '') or (form.query.data if form.validate_on_submit() else '')
        category_id = request.args.get('category_id', 0, type=int) or (form.category_id.data if form.validate_on_submit() else 0)
        min_price = request.args.get('min_price', type=float) or (form.min_price.data if form.validate_on_submit() else None)
        max_price = request.args.get('max_price', type=float) or (form.max_price.data if form.validate_on_submit() else None)
        location = request.args.get('location', '') or (form.location.data if form.validate_on_submit() else '')
        
        if query:
            ads = ads.filter(Ad.title.contains(query) | Ad.description.contains(query))
        if category_id:
            ads = ads.filter(Ad.category_id == category_id)
        if min_price is not None:
            ads = ads.filter(Ad.price >= min_price)
        if max_price is not None:
            ads = ads.filter(Ad.price <= max_price)
        if location:
            ads = ads.filter(Ad.location.contains(location))
    
    ads = ads.order_by(Ad.created_at.desc()).all()
    return render_template('search.html', form=form, ads=ads)


@app.route('/category/<int:category_id>')
def category_ads(category_id):
    """View ads by category"""
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    ads = Ad.query.filter_by(category_id=category_id, is_active=True).order_by(
        Ad.created_at.desc()
    ).paginate(page=page, per_page=12, error_out=False)
    return render_template('index.html', ads=ads, categories=Category.query.all(), current_category=category)


if __name__ == '__main__':
    app.run(debug=True)
