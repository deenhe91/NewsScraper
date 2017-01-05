#!flask/bin/python

from app import app
app.run(debug=True)

# have interface where user can input document, url perhaps?
# app processes content of document and returns topics and sentiment.