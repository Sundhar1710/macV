from app import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")
    priority = db.Column(db.String(50))  
    is_completed = db.Column(db.Boolean, default=False)
    assigned_user_email = db.Column(db.String(255), nullable=True)   
    due_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)

      

    def __init__(self, title, description, priority, due_date, user_id, project_id=None, assigned_user_email=None):
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.user_id = user_id
        self.project_id = project_id
        self.assigned_user_email = assigned_user_email
