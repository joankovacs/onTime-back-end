from app import db

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    time = db.Column(db.Integer) #<< time in minutes
    routine_id = db.Column(db.Integer, db.ForeignKey('routine.routine_id'), nullable=True)
    routine = db.relationship("Routine", back_populates="tasks")

    def to_dict(self):
        return {
            "id":self.task_id,
            "title":self.title,
            "time":self.time,
            "routine id":self.routine_id
            }
