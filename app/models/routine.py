from app import db

class Routine(db.Model):
    routine_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)

    def to_dict(self):
        return {
            "id":self.routine_id,
            "title":self.title,
            "desc":self.description,
            }

