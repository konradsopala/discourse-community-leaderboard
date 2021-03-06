# Imports

from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
import requests
import json
import os

# Global Setup

# TODO: Store those values in environment variables to retrieve them later (https://www.youtube.com/watch?v=5iWhQWVXosU)
# WEBHOOK_URL - Webhook URL for the Slack channel that you would like to post to
# ENDPOINT - URL of the endpoint that you're hitting executing your Data Explorer query
# API_KEY - Key that you can generate in API section in your Discourse Dashboard
# ACCOUNT_SID - Parameter that you can grab by logging into your Twilio Console (https://www.youtube.com/watch?v=knxlmCVFAZI)
# AUTH_TOKEN - Authentication token that you can grab from Twilio Console as well
# FROM_NUMBER - Your Twilio phone number that you will be sending the SMS from. Grab it from Twilio Console
# TO_NUMBER - Phone number that you will be sending the SMS to
# SENDGRID_KEY - Your API KEY that you can use to develop solutions using SendGrid services (https://www.youtube.com/watch?v=xCCYmOeubRE&t=19s)
# API_USERNAME - Put system if yoy created the API Key for all users otherwise put in your Discourse username

WEBHOOK_URL = os.environ['LEADERBOARD_WEBHOOK_URL']
ENDPOINT = os.environ['LEADERBOARD_ENDPOINT']
API_KEY = os.environ['LEADERBOARD_API_KEY']
ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
FROM_NUMBER = os.environ['TWILIO_LEADERBOARD_FROM_NUMBER']
TO_NUMBER = os.environ['TWILIO_LEADERBOARD_TO_NUMBER']
SENDGRID_KEY = os.environ['SENDGRID_KEY']
API_USERNAME = 'system'

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Core Functions

def fetch_leaderboard():

    headers = {'Content-Type': 'multipart/form-data', 'Api-Key': API_KEY, 'Api-Username': API_USERNAME}
    request = requests.post(url = ENDPOINT, headers = headers)
    print("Request Status Code: {}".format(request.status_code))

    # Unprocessed API request response

    response = json.loads(request.text)

    # Processed API request response - now it's parsed into a dictionary
    # TODO: Based on your query you will need to adjust the syntax below to access the dictionary element of your choice

    response_rows = response["rows"]

    first_place = {'Name': response_rows[0][1],
                   'Email': response_rows[0][2],
                   'Total_Points': response_rows[0][6]}

    second_place = {'Name': response_rows[1][1],
                   'Email': response_rows[1][2],
                   'Total_Points': response_rows[1][6]}

    third_place = {'Name': response_rows[2][1],
                   'Email': response_rows[2][2],
                   'Total_Points': response_rows[2][6]}

    winners_names_emails = [(first_place['Email'], first_place['Name']), (second_place['Email'], second_place['Name']),
                            (third_place['Email'], third_place['Name'])]

    response_text = "Community Leaderboard 🏆\n🥇 {} ({}) - {} pts\n🥈 {} ({}) - {} pts\n🥉 {} ({}) - {} pts".format(first_place['Name'], first_place['Email'], first_place['Total_Points'], second_place['Name'], second_place['Email'], second_place['Total_Points'], third_place['Name'], third_place['Email'], third_place['Total_Points'])

    # Output Form
    # Community Leaderboard 🏆
    # 🥇 John Doe (john.doe@gmail.com) - 51 pts
    # 🥈 Caroline Doe (caroline@yahoo.com) - 34 pts
    # 🥉 John Keller (johnkeller@gmail.com) - 12 pts

    return response_text, winners_names_emails

def post_to_slack(leaderboard):
    slack_message = {'text': leaderboard}
    requests.post(WEBHOOK_URL, json.dumps(slack_message))

def send_leaderboard_via_sms_to_prize_sender(leaderboard):
    message = twilio_client.messages.create(
        body = leaderboard,
        from_= FROM_NUMBER,
        to = TO_NUMBER)

def notify_top_contributors_via_email(leaderboard, winners_emails):

    # Whether if you want to hide your from email or not you can also store it in environment variables
    # TODO: Fill in from_email and adjust subject + html_content / plain_content based on your needs

    message = Mail(
        from_email = ('konrad.sopala@auth0.com', 'Konrad Sopala'),
        subject = 'Auth0 Community - Leaderboard 🏆',
        html_content = '',
        plain_text_content = 'Congrats for your efforts last month! We really appreciate it! You have been one of Top 3 performers in our community forum. Someone from Auth0 will contact you shortly to send you some secret SWAG\n{}'.format(leaderboard),
        to_emails = winners_emails,
        is_multiple = True)

    # Email Form
    # Congrats for your efforts last month! We really appreciate it! You have been one of Top 3 performers in our community forum.
    # Someone from Auth0 will contact you shortly to send you some secret SWAG!
    # Community Leaderboard 🏆
    # 🥇 John Doe (john.doe@gmail.com) - 51 pts
    # 🥈 Caroline Doe (caroline@yahoo.com) - 34 pts
    # 🥉 John Keller (johnkeller@gmail.com) - 12 pts

    sendgrid_client = SendGridAPIClient(SENDGRID_KEY)
    response = sendgrid_client.send(message)
    print(response.status_code)


processed_leaderboard = fetch_leaderboard()
post_to_slack(processed_leaderboard[0])
send_leaderboard_via_sms_to_prize_sender(processed_leaderboard[0])
notify_top_contributors_via_email(processed_leaderboard[0], processed_leaderboard[1])
