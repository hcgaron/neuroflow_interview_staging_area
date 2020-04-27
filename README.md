# Mood REST API

### Note on reviewing the stages of this app:

I created a different **branch** for the different stages of this app for your review!
The stages come in the order:

1. stage1
2. stage2Authentication
3. addStreakToBody
4. dockerize

The master branch has been merged with stage 4 and should contain the full working code. Tests begin in stage 3 since most code before that is boilerplate. I used the branches to make sure I would have backups, so you can check the final commit for each branch when reviewing.

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
5. **IMPORTANT**: open the src/neuroflow_rest_api/settings.py file:
   - Go to line **100** and change **`'HOST': 'db'`** to **`'HOST': 127.0.0.1`**
6. Run command **`python src/manage.py migrate`** to set up your database initially.
7. Run command **`python src/manage.py createsuperuser`** to create a super user profile for the web browsable API.
8. Run command **`python src/manage.py runserver`**

You are now up and running for on localhost:8000!

## Considerations for production

#### What would you do differently if this were a production environment and not an assessment?

The tests for this application reside in **src/mood/tests/test_views.py**. Tests can be run with **python src/manage.py test**, with all tests currently passing.

This app currently consists of boilerplate code to create accounts and log users in (using JWT authentication), and app-specific models & endpoints for creating **mood**s. I have written several tests for the app-specific **`/api/mood`** endpoint, but in production I would inevitably write many more tests for both authentication, and any additional mood functionality.

I would also split the tests a bit more to be more focused on single use cases rather than multiple **`assertEqual`** or similar assertions per test.

Furthermore, I would write more **`docstring`** comments in classes & methods for later reference. Since this app is so small, they would be a bit of overkill, but as this would likely be part of a larger app, **`docstring`**s would prove helpful.

I would also make use of **environment variables** rather than having things hard-coded into the src/neuroflow_rest_api/settings.py file. Environment variables would be loaded in via a script when the app is started.

Right now, the app is running on a **development server** which is **NOT** suitable for production. I would imaging we would use something like **Apache2** to serve this app. If using Apache2, I would use the src/neuroflow_rest_api/wsgi.py file to load environment variables from a script when the app is loaded.

#### Security

I would also change the JWT access token expiration time to a short value (5 - 20 mins) for security purposes, but allow refresh tokens to live as long as deemed safe to do so by project requirements.

Furthermore, I have currently allowed all CORS requests, but this wouldn't be suitbale for production. I would change the CORS_ORIGIN_WHITELIST to only allow from authorized addresses.

### Percentile Consieration

One interesting thing to note is that when calculating percentiles, Postgres offers a **PERCENT_RANK()** function. However, I instead decided to use the **CUME_DIST()** function which uses a [cumulative distribution function](https://en.wikipedia.org/wiki/Cumulative_distribution_function) to determine the relative standing of a data point. This has advantages and drawbacks. Postgres **PERCENT_RANK()** will decrease for datapoints that are tied (so if there are many data points tied for 1st place, their percentile will be roughly `1 / num_tied_data_points`). **CUME_DIST()** does not count this the same way, and gives a more appropriate ranking given the data we are using.

##### Percentile drawback for LARGE data set

But in production, the drawback is that querying the data is **expensive** if the data set grows very large. Django helps us with lazy evaluation of queries, and I've used **`.iterator`** when iterating over the query so that memory footprint will be low even for large datasets (**`.iterator()`** uses a generator when iterating over the `QuerySet`) but we still need to perform an aggregate SQL function over all the data for each MOOD request! This can be very expensive if the data set is huge!

So how to handle this more efficiently for large data sets?

#### Percentile proposal for LARGE data set

I would propose a nightly (or at least intervallic) recalculation of percentile buckets that can be cached and compared against users `streak`s. This could be scheduled with an asynchronous task scheduler like **celery**. Using Postgres **`NTILE(100)`** would yield values for each percentile which could be cached until the next evaluation. User streaks could then be compared against the values for each bucket to determine their percentile.

#### Other LARGE data set considerations

There are more optimizations that can be done for large data sets, some of which could be offloaded to the client side. For example, each day when the user signs in, we could automatically return the percentile buckets to them to be stored locally until the next day (or their next sign-in AFTER today). Then, many of the comparisons would be done on the client machine, saving time and cpu. This data would be lightweight (since it is only 100 values) and the comparisons would be easily handled even by mobile devices. That client would likely not even feel the effects of doing this calculation on their machine, but it may indeed speed up the API and speed up their experience since there is less likely a chance the API gets blocked / bombarded.

Additionally, the client side architecture (for example **React**) could expect the same properties returned in the data **regardless** of the current users streak. Then, that information could be used to display alerts / change UI based arbitrary conditions. Keeping the output consistent could lead to fewer client-side bugs where front-end developers are expecting data to be present but aren't receiving it because of a condition being checked on the back end.

#### What tech would you use?

I like using Django, Postgres, Apache, python, sklearn, TensorFlow & Keras (for machine learning), but these are all just tools and I'm open to other tech stacks. If I were tasked with taking on the full project myself I would probably use React for a browser based front-end and React Native for a cross-platform mobile app (to cut down on dev time for myself).

I could see benefits to using Flask, especially due to Django's opacity which, at one point in this assessment, caused a bit of a headache (I had to manually inspect the Django SQL queries being generated).

I would offload some of the expensive tasks (like intervallic calculation of percentiles) with an asynchronous task scheduler like celery & RabbitMQ. 
