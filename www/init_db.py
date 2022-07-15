from www import app, db

with app.test_request_context():
    db.drop_all()
    db.create_all()
