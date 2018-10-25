from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Data(db.Model):
    public_id = db.Column(db.String(50), primary_key=True)
    data = db.Column(db.BLOB())

    def __repr__(self):
        return '<Data {}>'.format(self.public_id)
