# for creating posts for users
# expects to be executied in flask application environment that contains all the app objects
users = User.query.all()
maxIterations = 10

for i in range(maxIterations):
   for u in users:
      b = 'My new test post: AB' + str(i)
      print ('Author: ' + u.username + b )
      p = Post(body=b, author=u)
      db.session.add(p)

db.session.commit()
