# Based on AHA Back-end Exam document
https://docs.google.com/document/d/15tA1qlVOg14cmpX0DbIPPnUQa9GYlSXcb9haRCojVEU/edit

# Install dependencies
python install -r requirements.txt

# Secret key for Flask
Execute `python -c "import os; print(os.urandom(20).hex())"`. \
Set the value of "SECRET_KEY" in ".env" file

# Google App Passwords
Go to your [Google Account](https://myaccount.google.com/). \
Activate 2-Step-Verification then generate an App Password. \
Set the values of "GMAIL_PASSWORD" and "GMAIL_ADDRESS" in ".env" file

# Google OAuth
Go to your [Google Console](https://console.developers.google.com/). \
Create an OAuth credential for "Web Application" with "Authorized redirect URIs" set to "{your_domain}/login/google/authorized". \
Download the json file as "google.json" in this current directory

# Facebook OAuth
Register as a [Facebook Developer](https://developers.facebook.com/docs/development/register/?locale=fr_FR). \
Create a "Customer" application. \
Copy the application ID & secret key in "App > Parameter > General". \
Set the values of "FACEBOOK_OAUTH_CLIENT_ID" and "FACEBOOK_OAUTH_CLIENT_SECRET" in ".env" file. \
Configure your app to use "Facebook Login" for "www". \
If your domain is not "localhost", configure the "Valid OAuth redirect URI" with "{your_domain}/login/facebook/authorized".

# Create/reset the database
python www/init_db.py

# Start the dev web server
flask run

# TODO
- [x] Email/Password signup
- [x] Send email verification
- [x] Login/Logout
- [x] User profile
- [x] Reset password
- [x] Dashboard
- [x] User statistics
- [x] Google OAuth signup/login
- [x] Facebook OAuth signup/login
- [x] Verify OAuth account automatically -> no email verification
- [ ] Merge account (email/pwd <-> oauth)
