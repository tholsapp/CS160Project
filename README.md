# CS160Project
CS160 Project

## Problem Statement

New airport shuttle services, “Let It Fly”, in the Bay Area counties (San Mateo,
Santa Clara, Alameda) needs a system to allow sub-contracted drivers to locate their next customer
request to/from one of the 3 airports (SFO, OAK, SJC). Requires mapping, time based traffic events, and
location based searches to guarantee the wait time to 30 minutes from the time of request.

You are responsible to develop the IT infrastructure and website for both the customer and driver.
Customer can go onto this website and request a ride.  The cost is based on distance and time (like how a
taxi works) with a minimum cost of $15 (first 2 miles are free).  The website will include logic to find the
next closest available driver based on real-time driving time to reach customer.  Once it does, it will
dispatch the drivers to the customer location.  Need to be able to track the driver and new customer
request via Google map.  Should use map services to calculate driving distances with travel and other
information included.

Special note: We use Google Map for routing.  Each driver can pick up 2 different parties if there are
open seats.  For example, customer A was picked up from SJSU to SFO.  On the path to SFO, customer B
requested a ride which is less than 1 miles off of the main driving path to SFO.  Driver then takes a detour
to pick up customer B before resuming the path to SFO.  If a driver picked up a 2nd party to airport, both
passenger parties will get a $5 discount.


## Requirements
Before you get started you'll need to have Python 2.6+ installed. After, you'll
need to also install virtualenv. Research how to do this for whatever platform
you run before continuing.

## Flask Web Sever
So far we have a Flask web server application.

Some notable parts used in this web application are:

  1. [Flask](http://flask.pocoo.org/)
  2. [Flask-Restless](https://flask-restless.readthedocs.org/en/latest/)
  3. [Flask-SQLAlchemy](https://pythonhosted.org/Flask-SQLAlchemy/)
  4. [Flask-Bootstrap](http://pythonhosted.org/Flask-Bootstrap/)
  5. [Flask-Script](http://flask-script.readthedocs.org/en/latest/)
  6. ... Other libraries used

## Install virtualenv and environment setup
It is recommended to use virtualenv when developing Flask applications,
also be sure you are using the most current version of pip

```bash
pip install --upgrade pip
pip install virtualenv
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

## Starting the application
Before you start the application be sure to set up your environment
described under "Install virtualenv and environment setup"

To run the application:
```bash
python manage.py runserver
```
Then, in your browser, navigate to http://127.0.0.1:5000/. You should see
something like the following image.

## Testing the application
At this time setup and testing has only been performed on OSX

## Contributing
For contributing please do the following.
### Cloning the application
```bash
git clone https://github.com/tholsapp/CS160Project
```
You will need to enter your git credentials.
### Creating a working branch
```bash
git checkout -b <branch>
```
This will create a new branch and automatically change you current branch.
In order to to get back to the master,
```bash
git checkout master
```
or
```bash
git branch master
```
However for development you will strictly be modifying your branch only.
You will never change anything in the master branch.
### Making changes
Before making changes be sure to type in,
```bash
git status
```
The first line should read,
```bash
On branch <your-branch>
```
If not, change or make your new branch.

To make a change simply change any file. In order to keep merges simple,
be sure only change one feature at a time.
### Adding you changes
After you have modified a file, if you type in git status
```bash
git status
On branch <branch>
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

        modified:   README.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)

  	<file/directory>

no changes added to commit (use "git add" and/or "git commit -a")
```
If you have modified or created a new file, you will need to add that
file or directory
```bash
git add <file/dirctory>
```
### Commiting you changes
After you have added your file(s) or directory(s),
```bash
git status
On branch tholsapp.branch
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

        modified:   README.md
```
This lists the file that is ready for the commit. To commit,
```bash
git commit -m "<message>"
```
Here, git commit will create a commit, -m is accept a command line argument message,
the message should be concise and accurate.
### Creating a pull request
Remember that you have just made these changes to you current branch, the actual code
on github has not been changed, however we might not want anyone to be able to change
the code without anyone else looking at it first. A pull request will alert that there
are changes that need to be looked over before actually being changed one github. After
a pull request if everything looks good, the code will then be merged, then the changes
have been made to all the code.
To create a pull request
```bash
git push origin <your-branch>
```
You will enter your git credentials, and I will be alerted that there are changes that
need to be looked over.
