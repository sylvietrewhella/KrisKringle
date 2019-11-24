import csv
import random
from random import randint
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
from string import Template

# email credentials
MY_ADDRESS = 'example@email.com'
PASSWORD = 'password'


class Participant(object):
    """
    Represent a Kris Kringle participant including their name, email address,
    partner and giftee.
    """

    def __init__(self, name, email, partner, giftee):
        self.name = name
        self.email = email
        self.partner = partner
        self.giftee = giftee

    def __str__(self):
        return f'{self.name}: {self.email} is giving to => {self.giftee}'

    def __eq__(self, other):
        return self.name == other.name

    def is_partner(self, other):
        return (self.partner == other.name)


def read_participants(file_name):
    """
    Reads participants from a csv file with their names, emails, and partners
    """
    participants = []
    with open(file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            participants.append(Participant(row[0], row[1], row[2], "?"))
        return participants


def assign_person(participants):
    """
    Assigns a giftee to each participant from the passed list.
    Participant cannot give a present to themselves or their partner
    """
    random.shuffle(participants)
    giftees = participants.copy()
    for p in participants:
        sucess = False
        while not sucess:
            random_index = randint(0, len(giftees)-1)
            giftee = giftees[random_index]
            # participant cannot give present to themselves or their partner
            if ((p != giftee) and (not p.is_partner(giftee))):
                p.giftee = giftee.name
                del giftees[random_index]
                sucess = True
            elif len(giftees) < 2:
                print(
                    f'{p.name} cannot be {giftee.name}\'s Kris Kringe. Try again!')
                return -1
    return participants


def print_participants(participants):
    """
    Prints the number and details lists of praticipants
    """
    print(f'Participants:')
    for p in participants:
        print(f'\t {p}')
    print(f'Processed {len(participants)} lines')


def send_email(msg):
    """
    Sets up the SMTP server to send emails specifided by the
    passed message (msg) parameter.
    """
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(MY_ADDRESS, PASSWORD)
    s.send_message(msg, rcpt_options=['NOTIFY=SUCCESS'])
    print("message sent to " + msg['To'])


def format_email(recipinent):
    """
    Formats email from template and customises the message
    based on the reciever.
    """
    message_template = read_template('message.txt')
    print(recipinent)
    message = message_template.substitute(
        PERSON_NAME=recipinent.name, GIFTEE_NAME=recipinent.giftee)
    msg = EmailMessage()
    msg['Subject'] = "Subject"
    msg['From'] = Address("Name", MY_ADDRESS)
    msg['To'] = (Address(recipinent.name, recipinent.email))
    msg.set_content(message)
    return msg


def read_template(filename):
    """
    Returns a Template object containing message from 
    the passed filename.
    """
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


# read all participants from file
participants = read_participants('participants.csv')
# assign participants a giftee
assigned_p = assign_person(participants)

# if siccessfull, send email to all participants
if assigned_p != -1:
    for p in assigned_p:
        msg = format_email(p)
        send_email(msg)

# confirm giver - giftee pairs
print("-----------------------------------")
print_participants(assigned_p)
