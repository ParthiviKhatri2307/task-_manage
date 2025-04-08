from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2307@localhost:2307/taskmaster'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)


# Models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='assigned_user_rel', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='todo')  # todo, in_progress, completed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)
    assigned_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)  # New field to track completion time

    def __repr__(self):
        return f'<Task {self.title}>'

    def to_dict(self):
        # Get user's name if assigned
        user_name = None
        if self.assigned_user:
            user = User.query.get(self.assigned_user)
            if user:
                user_name = user.full_name

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'assigned_user': self.assigned_user,
            'assigned_user_name': user_name,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


# Function to set up the database
def setup_db():
    # Create all tables
    db.create_all()

    # Check if we need to add demo data
    if not User.query.filter_by(email='john_doe@example.com').first():
        # Create demo users
        users = [
            {'full_name': 'John Doe', 'email': 'john_doe@example.com', 'password': 'password123'},
            {'full_name': 'Jane Smith', 'email': 'jane_smith@example.com', 'password': 'password123'},
            {'full_name': 'Mark Jones', 'email': 'mark_jones@example.com', 'password': 'password123'},
            {'full_name': 'Lisa Adams', 'email': 'lisa_adams@example.com', 'password': 'password123'},
            {'full_name': 'Emma Watson', 'email': 'emma_watson@example.com', 'password': 'password123'},
            {'full_name': 'Robert Brown', 'email': 'robert_brown@example.com', 'password': 'password123'}
        ]

        for user_data in users:
            user = User(
                full_name=user_data['full_name'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password'])
            )
            db.session.add(user)

        db.session.commit()

        # Get user IDs for assigning tasks
        john = User.query.filter_by(email='john_doe@example.com').first()
        jane = User.query.filter_by(email='jane_smith@example.com').first()
        mark = User.query.filter_by(email='mark_jones@example.com').first()
        lisa = User.query.filter_by(email='lisa_adams@example.com').first()
        emma = User.query.filter_by(email='emma_watson@example.com').first()
        robert = User.query.filter_by(email='robert_brown@example.com').first()

        # Create demo tasks based on your specifications
        tasks = [
            {
                'title': 'Data Backup',
                'description': 'Backup database daily',
                'status': 'completed',
                'priority': 'high',
                'created_at': datetime(2025, 3, 31),
                'due_date': datetime(2025, 4, 7).date(),
                'assigned_user': john.id,
                'completed_at': datetime(2025, 4, 1)
            },
            {
                'title': 'Security Audit',
                'description': 'Review system security',
                'status': 'completed',
                'priority': 'medium',
                'created_at': datetime(2025, 3, 30),
                'due_date': datetime(2025, 4, 15).date(),
                'assigned_user': jane.id,
                'completed_at': datetime(2025, 4, 2)
            },
            {
                'title': 'API Performance Test',
                'description': 'Run load tests on APIs',
                'status': 'completed',
                'priority': 'high',
                'created_at': datetime(2025, 3, 28),
                'due_date': datetime(2025, 4, 10).date(),
                'assigned_user': mark.id,
                'completed_at': datetime(2025, 4, 3)
            },
            {
                'title': 'Code Review',
                'description': 'Review PRs and merge pending code',
                'status': 'completed',
                'priority': 'medium',
                'created_at': datetime(2025, 3, 29),
                'due_date': datetime(2025, 4, 5).date(),
                'assigned_user': lisa.id,
                'completed_at': datetime(2025, 4, 4)
            },
            {
                'title': 'Server Update',
                'description': 'Update production servers',
                'status': 'completed',
                'priority': 'high',
                'created_at': datetime(2025, 4, 1),
                'due_date': datetime(2025, 4, 3).date(),
                'assigned_user': john.id,
                'completed_at': datetime(2025, 4, 2)
            },
            {
                'title': 'Error Log Analysis',
                'description': 'Analyze recent server errors',
                'status': 'todo',
                'priority': 'low',
                'created_at': datetime(2025, 3, 31),
                'due_date': datetime(2025, 4, 7).date(),
                'assigned_user': emma.id,
                'completed_at': None
            },
            {
                'title': 'Feature Deployment',
                'description': 'Deploy new feature release',
                'status': 'todo',
                'priority': 'critical',
                'created_at': datetime(2025, 4, 2),
                'due_date': datetime(2025, 4, 5).date(),
                'assigned_user': robert.id,
                'completed_at': None
            }
        ]

        for task_data in tasks:
            task = Task(**task_data)
            db.session.add(task)

        db.session.commit()


# Serve HTML files
@app.route('/')
def index():
    return send_from_directory('templates', 'login.html')


@app.route('/register')
def register_page():
    return send_from_directory('templates', 'register.html')


@app.route('/dashboard')
def dashboard():
    return send_from_directory('templates', 'dashboard.html')


@app.route('/<path:path>')
def serve_html(path):
    return send_from_directory('templates', path)


# API Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json

        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"detail": "Email already registered"}), 400

        user = User(
            full_name=data['full_name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password'])
        )

        db.session.add(user)
        db.session.commit()

        # Generate access token for immediate login
        access_token = create_access_token(identity=user.id)

        return jsonify({
            "message": "User registered successfully",
            "access_token": access_token,
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"detail": f"Registration error: {str(e)}"}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json

        user = User.query.filter_by(email=data['email']).first()

        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({"detail": "Invalid credentials"}), 401

        access_token = create_access_token(identity=user.id)

        return jsonify({
            "access_token": access_token,
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name
        })
    except Exception as e:
        return jsonify({"detail": f"Login error: {str(e)}"}), 500


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_user_info():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"detail": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name
    })


@app.route('/api/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    limit = request.args.get('limit', type=int)

    query = Task.query

    # Filter by status if provided
    status = request.args.get('status')
    if status:
        query = query.filter(Task.status == status)

    # Filter by assigned user if provided
    assigned_user = request.args.get('assigned_user')
    if assigned_user:
        query = query.filter(Task.assigned_user == assigned_user)

    # Sort by due date
    query = query.order_by(Task.due_date.asc())

    # Apply limit if provided
    if limit:
        query = query.limit(limit)

    tasks = query.all()

    return jsonify([task.to_dict() for task in tasks])


@app.route('/api/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.json

    due_date = None
    if 'due_date' in data and data['due_date']:
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()

    # If assigned_user is not provided, assign to current user
    assigned_user = data.get('assigned_user', user_id)

    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'todo'),
        priority=data.get('priority', 'medium'),
        due_date=due_date,
        assigned_user=assigned_user,
        created_at=datetime.utcnow()  # Use real-time date
    )

    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return jsonify({"detail": "Task not found"}), 404

    return jsonify(task.to_dict())


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.get(task_id)

    if not task:
        return jsonify({"detail": "Task not found"}), 404

    data = request.json

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.priority = data.get('priority', task.priority)

    # Handle status changes - if marking as completed, set completed_at timestamp
    new_status = data.get('status', task.status)
    if new_status == 'completed' and task.status != 'completed':
        task.completed_at = datetime.utcnow()
    elif new_status != 'completed':
        task.completed_at = None

    task.status = new_status

    if 'due_date' in data and data['due_date']:
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()

    if 'assigned_user' in data:
        task.assigned_user = data['assigned_user']

    db.session.commit()

    return jsonify(task.to_dict())


# New endpoint to specifically mark a task as complete
@app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
@jwt_required()
def complete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.get(task_id)

    if not task:
        return jsonify({"detail": "Task not found"}), 404

    # Mark as completed and set completion timestamp
    task.status = 'completed'
    task.completed_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "message": "Task marked as completed",
        "task": task.to_dict()
    })


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return jsonify({"detail": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"})


@app.route('/api/tasks/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    user_id = get_jwt_identity()

    # Get all tasks
    total = Task.query.count()
    todo = Task.query.filter_by(status='todo').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    completed = Task.query.filter_by(status='completed').count()

    # Get tasks specific to the current user if requested
    my_tasks = request.args.get('my_tasks', 'false').lower() == 'true'

    if my_tasks:
        total = Task.query.filter_by(assigned_user=user_id).count()
        todo = Task.query.filter_by(assigned_user=user_id, status='todo').count()
        in_progress = Task.query.filter_by(assigned_user=user_id, status='in_progress').count()
        completed = Task.query.filter_by(assigned_user=user_id, status='completed').count()

    # Get weekly completion data
    today = datetime.utcnow().date()
    start_of_week = today - timedelta(days=today.weekday())

    weekly_completion = []
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    for i in range(7):
        day = start_of_week + timedelta(days=i)

        # Use completed_at instead of created_at for completion stats
        count = Task.query.filter(
            Task.status == 'completed',
            db.func.date(Task.completed_at) == day
        ).count()

        weekly_completion.append({
            'day': days[i],
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })

    # Get priority distribution
    priority_stats = {
        'low': Task.query.filter_by(priority='low').count(),
        'medium': Task.query.filter_by(priority='medium').count(),
        'high': Task.query.filter_by(priority='high').count(),
        'critical': Task.query.filter_by(priority='critical').count()
    }

    return jsonify({
        'total': total,
        'todo': todo,
        'in_progress': in_progress,
        'completed': completed,
        'weekly_completion': weekly_completion,
        'priority_stats': priority_stats
    })


@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email
    } for user in users])


# Get current date and time
@app.route('/api/datetime', methods=['GET'])
def get_datetime():
    now = datetime.utcnow()
    return jsonify({
        'datetime': now.isoformat(),
        'date': now.date().isoformat(),
        'time': now.time().isoformat(),
        'timestamp': now.timestamp()
    })


if __name__ == '__main__':
    # Instead of using before_first_request, run setup_db within app_context
    with app.app_context():
        db.create_all()
        # Call our setup function to create demo data
        setup_db()
    app.run(debug=True)