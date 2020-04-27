# Mood REST API

## Quickstart

To quickly get up and started with this application be sure you have both
[docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/) installed on your machine.

Also ensure that docker is running locally. On Linux, you can run `systemctl status docker` to see if docker is running. Looking for a great linux distribution? I recommend [ZorinOS](https://zorinos.com/)!

1. Clone this repository to you local machine
2. Open your terminal and navigate to the project directory
3. Run command **`sudo docker-compose run web python src/manage.py migrate`** to set up the database.
4. Run command **`sudo docker-compose run web python src/manage.py createsuperuser`** to set up
   a super user profile for the web-browsable API.
5. Run command **`sudo docker-compose up`** to start the service listening on port `8000`

You are now up and running!

## Using the web browsable API.

To check out the API open your browser to **`http://localhost:8000/api/mood/`** and log in with the super user account you created in step 4.

Try posting a few moods! These are `POST` requests to the `api/mood/` endpoint. Each mood you post will persist in the database and will return the mood object you just created with a few statistics about the logged in user.

After you post a few moods, click the `GET` button at the top right of the page. This is a simple `GET` request to the `api/mood/` endpoint which will return a list of all of the logged in users posted moods.

## How to run without docker

To do this, you will need to have [PostgreSQL](https://www.postgresql.org/download/) installed and running on your machine on port `5432` (this is default, so you probably won't need to change that).

This app is simple enough to run locally without docker:

1. Clone this repository to your local machine
2. Open your terminal and navigate to the project directory
3. Make a virtual environment with [virtualenv](https://aaronlelevier.github.io/virtualenv-cheatsheet/) by running **`python3 -m venv venv`**
4. Activate your virtual environment with **`source venv/bin/activate`**
5. Run command **`python src/manage.py migrate`** to set up your database initially.
6. Run command **`python src/manage.py createsuperuser`** to create a super user profile for the web browsable API.
