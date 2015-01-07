# This is a sample local settings file.

# You MUST define the secret key, and make it unique for your own copy.
# One way is to run md5sum on a long randomly produced paragraph of text.
SECRET_KEY = 'f791c878c376cb54c3a28304d3342fe8f791c878c376cb54c3a28304d3342fe8'

# You'll also need to set the redirect uri in your 23andme API account to
# the correct path and port your app is listening on, eg. (for local dev):
# http://localhost:8000/file_process/receive_23andme/

REDIRECT_URI = 'add redirect uri here'
CLIENT_ID_23ANDME = 'client ID from 23andme API developer account'
CLIENT_SECRET_23ANDME = 'client secret from 23andme API developer account'
