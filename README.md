# Luna: Simple Monitoring For Invisible Devices And Services
[![Build Status](https://app.travis-ci.com/avrilmaomao/lunakeeper.svg?branch=master)](https://app.travis-ci.com/avrilmaomao/lunakeeper)
[![Coverage Status](https://coveralls.io/repos/github/avrilmaomao/lunakeeper/badge.svg?branch=master)](https://coveralls.io/github/avrilmaomao/lunakeeper?branch=dev)

**Luna** is a simple monitoring system for *invisible* devices or services, like a RaspberryPi in your home or a scheduled task. It checks whether a monitored item is able to send requests during the required interval.

![Luna Working FLow](https://docs.google.com/drawings/d/e/2PACX-1vSTG1VyblXbcN_uBryJoOUzdgH2JabprC_eTNPZRxSb29w06qu1bQJvrnFRJgjov3LNxAAGpN8BYxXU/pub?w=306&h=255)

## Luna can be used for
- checking a RaspberryPi is running with internet connection
- checking a scheduled task is triggered regularly
- checking the status of an application not listening ports

## Supported notification types
When Luna finds a monitored item missing, she will send you a notification. You can specify your notification info when adding or changing a monitored item.

- Email 
- Slack

## Requirements
- the monitored item can send HTTP **GET** requests at a regular interval
- the monitored item has an internet connection or can reach the Luna server

## Develop and Deploy
Luna is developed using [Django](https://www.djangoproject.com/), the development and deployment process is just like normal Django apps. However,there are a few things that need to be taken special care of.
#### 1.Settings for different environments
- Luna uses production settings if an environment variable **DJANGO_PRODUCTION** is set , otherwise she uses development settings.
- add `luna/settings_prod.py` file to add or override settings for production (Required). An example of `settings_prod.py`(`settings_prod.py.example`) is included for ease of use.
- add `luna/settings_dev.py` file to add or override settings for development (Optional).

#### 2.The Commands for checking monitored items
Luna uses a Django management command `checkpony` to check monitored items and send notifications. In production, you need to run this command every 5 minutes(using crontab under unix like system or Task Scheduler under Windows).

A Linux crontab example:
`*/5 * * * * DJANGO_PRODUCTION=1 python management.py checkpony` 

(don't forget to set environment variable **DJANGO_PRODUCTION** ,if you are using it in production deployment. )

#### 3. If you are not familiar with Django, you can follow [this step-to-step guide](https://github.com/avrilmaomao/lunakeeper/wiki/How-to-deploy-Luna-on-a-Linux-server-with-Ubuntu,-Python,-Nginx,-Gunicorn-and-Django) to set up Luna in production(though basic Linux and database skills needed).

## How to use
After deployment, navigate to Luna's index page in your browser. The index page will show the necessary steps and detailed api info for you to start monitoring.
