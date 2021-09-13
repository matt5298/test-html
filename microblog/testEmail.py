
from flask_mail import Message
from app import mail
msg = Message('test subject', sender=app.config['ADMINS'][0], recipients=['matt5298@gmail.com'])
msg.body = 'The body of an email'
msg.html = '<h1>HTML body</h1>'
mail.send(msg)

