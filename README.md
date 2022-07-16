# Based on AHA Back-end Exam document
https://docs.google.com/document/d/15tA1qlVOg14cmpX0DbIPPnUQa9GYlSXcb9haRCojVEU/edit

# Install dependencies
python install -r requirements.txt

# Create/reset the database
python www\init_db.py

# Start the dev web server
flask run

# TODO
[x] Email/Password signup
[x] Send email verification
[x] Login/Logout
[x] User profile
[x] Reset password
[x] Dashboard
[x] User statistics
[ ] Google OAuth signup
[ ] Facebook OAuth signup
[ ] Verify OAuth account automatically -> no email verification
