from app import db

class Routine(db.Model):
    routine_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    destination = db.Column(db.String) #<< Location object?

    complete_time = db.Column(db.DateTime)
    start_time = db.Column(db.DateTime)  #Calculated from complete time
    total_time = db.Column(db.Integer) #<< number of minutes, calculated

    saved = db.Column(db.Boolean) #defaults to True
    tasks = db.relationship("Task", back_populates="routine", lazy=True)


    def to_dict(self):
        return {
            "routine_id":self.routine_id,
            "title":self.title,
            "description":self.description,
            "destination":self.destination,

            "complete_time":self.complete_time,
            "start_time":self.start_time,
            "total_time":self.total_time,

            "saved":self.saved,
            "tasks":[task.to_routine() for task in self.tasks]
            }

