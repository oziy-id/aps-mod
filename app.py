import os
import io
import functools
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response 
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'kunci-rahasia-default')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database Config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload Settings
    ALLOWED_EXTENSIONS = {'apk', 'xapk', 'zip'}
    
    # Email Config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT')

    # Supabase Config
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    SUPABASE_BUCKET = "uploads" 

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# --- SUPABASE CLIENT ---
supabase: Client = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

# --- UTILS ---
def get_wib_now():
    return datetime.utcnow() + timedelta(hours=7)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def allowed_media(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'webp', 'pdf'}

# --- FUNGSI KOMPRES GAMBAR ---
def compress_image(file_storage, is_icon=False):
    try:
        img = Image.open(file_storage)
        output = io.BytesIO()
        if is_icon:
            img.thumbnail((512, 512)) 
            img.save(output, format='WEBP', quality=90)
            new_filename = file_storage.filename.rsplit('.', 1)[0] + ".webp"
            mimetype = 'image/webp'
        else:
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            img.thumbnail((1280, 720)) 
            img.save(output, format='JPEG', quality=80, optimize=True)
            new_filename = file_storage.filename.rsplit('.', 1)[0] + ".jpg"
            mimetype = 'image/jpeg'
        output.seek(0)
        return output, new_filename, mimetype
    except Exception as e:
        print(f"Gagal kompres gambar: {e}")
        file_storage.seek(0)
        return file_storage, file_storage.filename, getattr(file_storage, 'content_type', 'application/octet-stream')

def upload_to_supabase(file, filename, content_type):
    try:
        file_content = file.read()
        res = supabase.storage.from_(app.config['SUPABASE_BUCKET']).upload(
            path=filename,
            file=file_content,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        return True
    except Exception as e:
        print(f"Supabase Upload Error: {e}")
        return False

def get_supabase_url(filename):
    return supabase.storage.from_(app.config['SUPABASE_BUCKET']).get_public_url(filename)

def delete_from_supabase(filename):
    try:
        supabase.storage.from_(app.config['SUPABASE_BUCKET']).remove([filename])
    except Exception as e:
        print(f"Supabase Delete Error: {e}")

# --- EMAIL SENDER ---
def send_email(subject, recipient, template, **kwargs):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"APSMod System <{app.config['MAIL_USERNAME']}>"
        msg['To'] = recipient
        msg['Subject'] = subject
        html_body = render_template(template, **kwargs)
        msg.attach(MIMEText(html_body, 'html'))
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.sendmail(app.config['MAIL_USERNAME'], recipient, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"EMAIL ERROR: {e}")
        return False

# --- MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='partner')
    created_at = db.Column(db.DateTime, default=get_wib_now)
    reset_token = db.Column(db.String(10), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

class InviteCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20))
    category = db.Column(db.String(50))
    size = db.Column(db.String(20))
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500)) 
    icon_path = db.Column(db.String(200))
    is_featured = db.Column(db.Boolean, default=False)
    screenshot_path = db.Column(db.String(200)) 
    screenshot_orient = db.Column(db.String(20), default='landscape')
    screenshots = db.relationship('AppScreenshot', backref='app', lazy=True, cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='app', lazy=True, cascade="all, delete-orphan")
    downloads = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=4.5)
    created_at = db.Column(db.DateTime, default=get_wib_now)
    uploader_email = db.Column(db.String(120))

class AppScreenshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    orientation = db.Column(db.String(20), default='landscape')

# [UPDATE] Model Komentar dengan Parent ID (Reply System)
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    is_developer = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_wib_now)
    # Kolom untuk Reply
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50))
    app_name = db.Column(db.String(100))
    details = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=get_wib_now)

# --- SETUP & DECORATORS ---
def create_initial_data():
    if not User.query.filter_by(role='owner').first():
        hashed_pw = generate_password_hash("Oziyy77/394")
        owner = User(email="oziyy77@gmail.com", password_hash=hashed_pw, role='owner')
        db.session.add(owner)
    if not InviteCode.query.first():
        initial_code = os.environ.get('INVITE_CODE', '6453')
        db.session.add(InviteCode(code=initial_code))
    db.session.commit()

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session: return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            flash('Akun Anda telah dinonaktifkan.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def log_activity(action, app_name, details):
    try:
        new_log = ActivityLog(action=action, app_name=app_name, details=details, timestamp=get_wib_now())
        db.session.add(new_log)
        db.session.commit()
    except: pass

# --- ROUTES ---
@app.route('/')
def index():
    search_query = request.args.get('q')
    category_query = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    per_page = 12 

    query = Application.query
    if search_query: query = query.filter(Application.title.ilike(f'%{search_query}%'))
    if category_query: query = query.filter_by(category=category_query)
    
    paginated_apps = query.order_by(Application.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    featured_apps = Application.query.filter_by(is_featured=True).order_by(Application.created_at.desc()).limit(5).all()
    popular_apps = Application.query.order_by(Application.downloads.desc()).limit(5).all()
    
    return render_template('index.html', apps=paginated_apps, featured_apps=featured_apps, popular_apps=popular_apps, search_query=search_query, current_category=category_query)

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name') 
        email = request.form.get('email')
        message = request.form.get('message')
        if send_email(f"Pesan Baru dari {name}", app.config['MAIL_RECIPIENT'], 'email.html', name=name, user_email=email, message=message):
            flash('Pesan berhasil dikirim!', 'success')
        else:
            flash('Gagal mengirim pesan.', 'error')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/app/<int:app_id>')
def detail(app_id):
    app = Application.query.get_or_404(app_id)
    is_pdf_icon = app.icon_path and app.icon_path.lower().endswith('.pdf')
    # [UPDATE] Hanya ambil komentar INDUK (yang tidak punya parent)
    comments = Comment.query.filter_by(app_id=app_id, parent_id=None).order_by(Comment.created_at.desc()).all()
    return render_template('detail.html', app=app, is_pdf_icon=is_pdf_icon, comments=comments)

# [UPDATE] Route Kirim Komentar + Reply
@app.route('/app/<int:app_id>/comment', methods=['POST'])
def add_comment(app_id):
    app_obj = Application.query.get_or_404(app_id)
    content = request.form.get('content')
    parent_id = request.form.get('parent_id') # Ambil ID Parent jika ada
    
    # Validasi Parent ID (Pastikan kosong string jadi None)
    if parent_id == "": parent_id = None
    
    # Cek apakah user adalah Developer/Partner
    is_dev = 'user_id' in session
    
    if is_dev:
        role = session.get('role', 'partner')
        if role == 'owner':
            name = "Developer"
        else:
            name = "Team Partner"
        is_developer = True
    else:
        name = request.form.get('name')
        is_developer = False
        
        # [ANTI SPAM]
        last_comment_time = request.cookies.get('last_comment_time')
        if last_comment_time:
            try:
                last_time = datetime.fromtimestamp(float(last_comment_time))
                if datetime.now() - last_time < timedelta(minutes=30):
                    flash('Tunggu 30 menit sebelum komentar lagi!', 'error')
                    return redirect(url_for('detail', app_id=app_id))
            except: pass

    if content:
        new_comment = Comment(
            app_id=app_id, 
            name=name, 
            content=content, 
            is_developer=is_developer,
            parent_id=parent_id # Masukkan parent_id
        )
        db.session.add(new_comment)
        
        # [AUTO CLEANER]
        thirty_days_ago = get_wib_now() - timedelta(days=30)
        old_comments = Comment.query.filter(Comment.created_at < thirty_days_ago).delete()
        
        db.session.commit()
        flash('Komentar terkirim!', 'success')
    
    resp = make_response(redirect(url_for('detail', app_id=app_id)))
    if not is_dev:
        expire_date = datetime.now() + timedelta(minutes=30)
        resp.set_cookie('last_comment_time', str(datetime.now().timestamp()), expires=expire_date)
        
    return resp

@app.route('/download/<int:app_id>')
def download_file(app_id):
    app_obj = Application.query.get_or_404(app_id)
    app_obj.downloads += 1
    db.session.commit()
    return redirect(app_obj.file_path)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return redirect(get_supabase_url(filename))

# --- AUTH & PASSWORD RESET ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session: return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['email'] = user.email
            return redirect(url_for('admin_dashboard'))
        flash('Email atau Password salah.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session: return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        otp_input = request.form.get('otp')
        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar.', 'error')
            return redirect(url_for('register'))
        valid_code = InviteCode.query.first()
        if not valid_code or otp_input != valid_code.code:
            flash('Kode OTP Salah.', 'error')
            return redirect(url_for('register'))
        new_partner = User(email=email, password_hash=generate_password_hash(password), role='partner')
        db.session.add(new_partner)
        db.session.commit()
        flash('Registrasi Berhasil.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            otp = ''.join(random.choices(string.digits, k=6))
            user.reset_token = otp
            user.reset_token_expiry = get_wib_now() + timedelta(minutes=15)
            db.session.commit()
            send_email("Reset Password - APSMod", email, 'email_reset.html', otp=otp)
            flash('Kode OTP telah dikirim ke email Anda.', 'success')
            return redirect(url_for('reset_password', email=email))
        else:
            flash('Email tidak terdaftar sebagai partner.', 'error')
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email') or request.form.get('email')
    if request.method == 'POST':
        otp_input = request.form.get('otp')
        new_password = request.form.get('new_password')
        user = User.query.filter_by(email=email).first()
        if user:
            if user.reset_token == otp_input and user.reset_token_expiry > get_wib_now():
                user.password_hash = generate_password_hash(new_password)
                user.reset_token = None
                user.reset_token_expiry = None
                db.session.commit()
                flash('Password berhasil diubah! Silakan login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Kode OTP salah atau sudah kadaluarsa.', 'error')
        else:
            flash('Terjadi kesalahan.', 'error')
    return render_template('reset_password.html', email=email)

# --- ADMIN DASHBOARD ---
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if request.method == 'POST':
        download_url = request.form.get('download_url')
        manual_size = request.form.get('size', '0 MB')
        icon_file = request.files.get('icon')
        screenshot_files = request.files.getlist('screenshots') 
        title_input = request.form.get('title')
        description_input = request.form.get('description')
        version_input = request.form.get('version', 'Latest')
        category_input = request.form.get('category', 'Games')
        orientation_input = request.form.get('orientation', 'landscape')
        is_featured_input = 'is_featured' in request.form
        
        if not title_input: return redirect(request.url)
        
        existing_app = Application.query.filter_by(title=title_input).first()
        app_obj = existing_app if existing_app else Application(title=title_input)
        
        if not existing_app:
            db.session.add(app_obj)
            log_activity("UPLOAD", title_input, f"By {session.get('email')}")
        else:
            log_activity("UPDATE", title_input, f"Updated by {session.get('email')}")
            
        if download_url:
            app_obj.file_path = download_url
            app_obj.size = manual_size
            
        if icon_file and allowed_media(icon_file.filename):
            compressed_file, new_name, new_mime = compress_image(icon_file, is_icon=True)
            icon_filename = secure_filename(f"icon_{datetime.now().timestamp()}_{new_name}")
            upload_to_supabase(compressed_file, icon_filename, new_mime) 
            app_obj.icon_path = icon_filename
            
        app_obj.description = description_input
        app_obj.version = version_input
        app_obj.category = category_input
        app_obj.is_featured = is_featured_input
        app_obj.uploader_email = session.get('email')
        app_obj.created_at = get_wib_now()
        db.session.commit()
        
        if screenshot_files and screenshot_files[0].filename != '':
            AppScreenshot.query.filter_by(app_id=app_obj.id).delete()
            for i, ss in enumerate(screenshot_files):
                if ss and allowed_media(ss.filename):
                    compressed_ss, ss_name, ss_mime = compress_image(ss, is_icon=False)
                    final_ss_name = secure_filename(f"ss_{datetime.now().timestamp()}_{ss_name}")
                    upload_to_supabase(compressed_ss, final_ss_name, ss_mime)
                    new_ss = AppScreenshot(app_id=app_obj.id, image_path=final_ss_name, orientation=orientation_input)
                    db.session.add(new_ss)
                    if i == 0:
                        app_obj.screenshot_path = final_ss_name
                        app_obj.screenshot_orient = orientation_input
            db.session.commit()
            
        flash('Data dipublikasikan!', 'success')
        return redirect(url_for('admin_dashboard'))

    apps = Application.query.order_by(Application.created_at.desc()).all()
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(15).all()
    partners = User.query.filter_by(role='partner').all() if session.get('role') == 'owner' else []
    otp_obj = InviteCode.query.first()
    current_otp = otp_obj.code if otp_obj else "Err"
    return render_template('admin/dashboard.html', apps=apps, logs=logs, partners=partners, current_otp=current_otp)

@app.route('/admin/kick_partner/<int:user_id>')
@login_required
def kick_partner(user_id):
    if session.get('role') != 'owner': return redirect(url_for('admin_dashboard'))
    target = User.query.get_or_404(user_id)
    if target.role != 'owner':
        db.session.delete(target)
        db.session.commit()
        flash(f'Team {target.email} telah dikeluarkan!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_otp', methods=['POST'])
@login_required
def update_otp():
    if session.get('role') != 'owner': return redirect(url_for('admin_dashboard'))
    new = request.form.get('new_code')
    otp = InviteCode.query.first()
    if otp: otp.code = new
    else: db.session.add(InviteCode(code=new))
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_link/<int:app_id>', methods=['POST'])
@login_required
def update_app_link(app_id):
    app_obj = Application.query.get_or_404(app_id)
    new_url = request.form.get('new_url')
    new_version = request.form.get('new_version') 
    if new_url and new_version:
        app_obj.file_path = new_url
        app_obj.version = new_version
        app_obj.created_at = get_wib_now()
        db.session.commit()
        flash('Link & Versi berhasil diperbarui!', 'success')
        log_activity("UPDATE APP", app_obj.title, f"v{new_version} By {session.get('email')}")
    else:
        flash('Link atau Versi tidak boleh kosong.', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:app_id>')
@login_required
def delete_app(app_id):
    app = Application.query.get_or_404(app_id)
    try:
        if app.icon_path: delete_from_supabase(app.icon_path)
        for ss in app.screenshots: delete_from_supabase(ss.image_path)
    except: pass
    db.session.delete(app)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_initial_data()
    app.run(debug=True, port=5000)
