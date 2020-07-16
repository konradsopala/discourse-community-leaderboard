# Discourse Community Leaderboard

![](/Assets/DiscourseLeaderboardCover.png)

<a href="https://www.discourse.org/"><img src="https://img.shields.io/badge/Discourse-Community-blueviolet" alt=""/></a>     <a href="https://www.discourse.org/plugins/data-explorer.html"><img src="https://img.shields.io/badge/Data-Explorer-blueviolet" alt=""/></a>   <a href="https://www.twilio.com/"><img src="https://img.shields.io/badge/Twilio-SMS-BLUEVIOLET" alt=""/></a> <a href="https://sendgrid.com/"><img src="https://img.shields.io/badge/SendGrid-Email-BLUEVIOLET" alt=""/></a> <a href="https://en.wikipedia.org/wiki/Cron"><img src="https://img.shields.io/badge/Cron-Scheduler-blueviolet" alt=""/></a>

Want to motivate your Discourse Community Top Contributors? They're performing exceptionally well by providing answers and solutions to others' question? Want to send them SWAG for that or any other kind of prize? Got you covered! At least on the technical side of things: fetching leaderboard, sending SMS summary to the SWAG sender in your company, posting top 3 contributors in Slack, notifying top contributors, . You just need to take care of the physical prize shipping!

This script will execute on the first day of every month, running your Leaderbord query, parsing its results, sending SMS with top three contributors with their names, email and total points to the person in your company responsible for SWAG shipment, posting the same content to the Slack channel of your choice, as well as notifying those top performers via email about their great work and prizes on their way.

**Fill in the script parameters once, deploy automatically every month!**

### Core Concept

The main concept here is to save your time on the manual work. You won't need to do those things anymore:

* Execute leaderboard query manually every month
* Copy-paste the results to let people in your company know who performed best in the community forum
* Sending the message with top contributors to the person in your company responsible for SWAG shipping
* Sending message to top performers with the info that they actually won something with their effort

Each of those steps will be automated, you just need to setup the script once.

**Saving time one query / SMS / email at a time!**

### The Leaderboard

The leaderboard SQL query was developed based on point system. Number of replies, solutions provided and likes received are taken into account. Here's how the point system works:

* Each **solution** provided - 3 points
* Each **reply** given - 2 points
* Each **like** received - 1 point

All that sums up and we have total points. Here's how example leaderboard look like:

![](/Assets/LeaderboardScreenshot.png)

### The Script

It was developed using Python, Twilio (SMS), SendGrid (Email), cron (Scheduling) . Full script code can be found [here](https://github.com/konradsopala/discourse-community-leaderboard/blob/master/Script/leaderboard.py). Simplified script code is shown below:

```
client = Client(ACCOUNT_SID, AUTH_TOKEN)

def fetch_leaderboard():

    headers = {'Content-Type': 'multipart/form-data', 'Api-Key': API_KEY, 'Api-Username': API_USERNAME}
    request = requests.post(url = ENDPOINT, headers = headers)

    response = json.loads(request.text)
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

    winners_names_emails = [(first_place['Email'], first_place['Name']), (second_place['Email'], second_place['Name']), (third_place['Email'], third_place['Name'])]

    response_text = "Community Leaderboard 🏆\n🥇 {} ({}) - {} pts\n🥈 {} ({}) - {} pts\n🥉 {} ({}) - {} pts".format(first_place['Name'], first_place['Email'], first_place['Total_Points'], second_place['Name'], second_place['Email'], second_place['Total_Points'], third_place['Name'], third_place['Email'], third_place['Total_Points'])

    return response_text, winners_names_emails

def post_to_slack(leaderboard):
    slack_message = {'text': leaderboard}
    requests.post(WEBHOOK_URL, json.dumps(slack_message))

def send_leaderboard_via_sms_to_prize_sender(leaderboard):
    message = client.messages.create(
        body = leaderboard,
        from_= FROM_NUMBER,
        to = TO_NUMBER)

def notify_top_contributors_via_email(leaderboard, winners_emails):
    message = Mail(
	from_email = ('konrad.sopala@auth0.com', 'Konrad Sopala'),
	subject = 'Auth0 Community - Leaderboard 🏆',
	html_content = '',
	plain_text_content = 'Congrats for your efforts last month! We really appreciate it! You have been one of Top 3 performers in our community forum. Someone from Auth0 will contact you shortly to send you some secret SWAG\n{}'.format(leaderboard),
	to_emails = winners_emails,
	is_multiple = True)

processed_leaderboard = fetch_leaderboard()
post_to_slack(processed_leaderboard[0])
send_leaderboard_via_sms_to_prize_sender(processed_leaderboard[0])
notify_top_contributors_via_email(processed_leaderboard[0], processed_leaderboard[1])
```

This method runs the Python script automatically provided that you scheduled that with cron (described below). Here are the steps to make the method work, assuming you have Python installed on your computer:

* Create your Slack Workspace by going to https://slack.com/get-started#/create
* Create a channel that you would like to send your stats to
* Go to https://yourWorkspaceName.slack.com/apps/manage
* In the search bar type in: Incoming WebHooks and click: Add Configuration
* Follow the instructions and copy the Webhook URL given at the end
* Download the [Python Script](https://github.com/konradsopala/discourse-community-leaderboard/blob/master/Script/leaderboard.py)
* Follow the instructions described in script's comments

To make it execute itself on the first day of each month at 12:00 automatically, go through following steps:

* Open terminal (Mac / Linux)
* Type in ```crontab -e```
* Press ```i``` to enable insert mode in Vim
* Copy and paste this snippet adjusting the path for where you downloaded your script:

```
0 12 1 * * cd <insert_script_folder_location_path> && python leaderboard.py

```
* Press esc and type ```:wq```

If you want to schedule the execution of the script at different time, follow this cron scheduling mechanism:
```
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday;
# │ │ │ │ │                                       7 is also Sunday on some systems)
# │ │ │ │ │
# │ │ │ │ │
# * * * * *  command_to_execute
```

![](/Assets/ScriptResults.png)

**Your post on Slack, SMS and EMAIL should be all there on the first day of each month at 12:00 your machine time! Congrats! 🎉**

### Supporting documentation

If you want to find out more about the stack used in those tools or even build your own tools, make sure to visit following links and get inspired:

* [Cron](https://en.wikipedia.org/wiki/Cron) <br>
* [Twilio SMS](https://www.twilio.com/docs/sms/quickstart/python) <br>
* [SendGrid Email](https://sendgrid.com/docs/for-developers/sending-email/v3-python-code-example/) <br>
* [Slack API](https://api.slack.com/) <br>
* [Discourse Forums](https://www.discourse.org/) <br>
* [Data Explorer Plugin](https://meta.discourse.org/t/data-explorer-plugin/32566) <br>
