from app import db

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    time = db.Column(db.Integer) #<< time in minutes
    start_time = db.Column(db.DateTime) #Normally empty until the associated Routine gets a complete time
    routine_id = db.Column(db.Integer, db.ForeignKey('routine.routine_id'), nullable=True)
    routine = db.relationship("Routine", back_populates="tasks")

    def datetime_to_clock(self):
        #returns hour and minute from the start_time
        if self.start_time:
            if self.start_time.hour == 12:
                meridiem = "PM"
                hour_time = self.start_time.hour
            elif self.start_time.hour > 12:
                meridiem = "PM"
                hour_time = self.start_time.hour-12
            else:
                meridiem = "AM"
                hour_time = self.start_time.hour

            return {
                "hour":hour_time,
                "minute":self.start_time.minute,
                "meridiem":meridiem,
                }
        else:
            return None


    def to_dict(self):
        return {
            "task_id":self.task_id,
            "title":self.title,
            "time":self.time,
            "start_time":self.datetime_to_clock(),
            "routine_id":self.routine_id
            }
