from app import app, db, Task, User
from datetime import datetime

def add_tasks():
    with app.app_context():
        # Get user IDs for assigning tasks
        john = User.query.filter_by(email='john_doe@example.com').first()
        jane = User.query.filter_by(email='jane_smith@example.com').first()
        mark = User.query.filter_by(email='mark_jones@example.com').first()
        lisa = User.query.filter_by(email='lisa_adams@example.com').first()
        emma = User.query.filter_by(email='emma_watson@example.com').first()
        robert = User.query.filter_by(email='robert_brown@example.com').first()

        # Check if tasks already exist to avoid duplicates
        if Task.query.filter_by(title='Data Backup').first():
            print("Tasks already exist in database. Skipping insertion.")
            return

        # Create tasks from the provided data
        tasks = [
            {
                'title': 'Data Backup',
                'description': 'Backup database daily',
                'status': 'completed',  # TRUE in your table
                'priority': 'high',     # HIGH in your table
                'created_at': datetime(2025, 3, 31),
                'due_date': datetime(2025, 4, 7).date(),  # Setting due date 7 days after creation
                'assigned_user': john.id if john else None
            },
            {
                'title': 'Security Audit',
                'description': 'Review system security',
                'status': 'completed',
                'priority': 'medium',
                'created_at': datetime(2025, 3, 30),
                'due_date': datetime(2025, 4, 7).date(),
                'assigned_user': jane.id if jane else None
            },
            {
                'title': 'API Performance Test',
                'description': 'Run load tests on APIs',
                'status': 'completed',
                'priority': 'high',
                'created_at': datetime(2025, 3, 28),
                'due_date': datetime(2025, 4, 5).date(),
                'assigned_user': mark.id if mark else None
            },
            {
                'title': 'Code Review',
                'description': 'Review PRs and merge pending code',
                'status': 'completed',
                'priority': 'medium',
                'created_at': datetime(2025, 3, 29),
                'due_date': datetime(2025, 4, 5).date(),
                'assigned_user': lisa.id if lisa else None
            },
            {
                'title': 'Server Update',
                'description': 'Update production servers',
                'status': 'completed',
                'priority': 'high',
                'created_at': datetime(2025, 4, 1),
                'due_date': datetime(2025, 4, 5).date(),
                'assigned_user': john.id if john else None
            },
            {
                'title': 'Error Log Analysis',
                'description': 'Analyze recent server errors',
                'status': 'todo',        # FALSE in your table
                'priority': 'low',       # LOW in your table
                'created_at': datetime(2025, 3, 31),
                'due_date': datetime(2025, 4, 7).date(),
                'assigned_user': emma.id if emma else None
            },
            {
                'title': 'Feature Deployment',
                'description': 'Deploy new feature release',
                'status': 'todo',
                'priority': 'critical',
                'created_at': datetime(2025, 4, 2),
                'due_date': datetime(2025, 4, 9).date(),
                'assigned_user': robert.id if robert else None
            }
        ]

        # Add tasks to database
        for task_data in tasks:
            task = Task(**task_data)
            db.session.add(task)

        # Commit changes
        db.session.commit()
        print("Successfully added tasks to database.")

if __name__ == "__main__":
    add_tasks()