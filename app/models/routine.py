from app import db

class Routine(db.Model):
    routine_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    destination = db.Column(db.String) #<< Location object?

    complete_time = db.Column(db.DateTime)
    start_time = db.Column(db.DateTime)  #Calculated from complete time
    total_time = db.Column(db.Integer, default=0) #<< number of minutes, calculated

    tasks = db.relationship("Task", back_populates="routine", lazy=True)


    def to_dict(self):
        return {
            "routine_id":self.routine_id,
            "title":self.title,
            "description":self.description,
            "destination": self.destination,

            "complete_time": self.complete_time,
            "start_time": self.start_time,
            "total_time":self.total_time,

            "tasks":[task.to_routine() for task in self.tasks]
            }

    def set_total_time(self):
        '''
        Method should run in endpoints any time the task list changes
        '''
        self.total_time = sum([task.time for task in self.tasks])
            
