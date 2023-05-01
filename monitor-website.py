import requests
import smtplib
import os
import paramiko
import boto3
import time
import schedule

EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
ec2_client = boto3.client('ec2', region_name="us-east-1")


def restart_container():
    # restart the app
    print('Restarting the app...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='18.215.165.157', username='admin', key_filename='/Users/moabdulhadi/.ssh/id_rsa')
    stdin, stdout, stderr = ssh.exec_command('sudo docker run -d -p 8080:80 nginx')
    print(stdout.readlines())
    ssh.close()
    print('App restarted')


def send_notification(email_msg):
    print('Sending an email...')
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        message = f'Subject: App is Down\n{email_msg}'
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)


def reboot_instance():
    print('Rebooting the server')
    response = ec2_client.reboot_instances(InstanceIds=['i-09bafc25406fa61e5'])
    print(response)


def monitor_app():
    try:
        response = requests.get('http://18.215.165.157:8080/')
        if response.status_code == 200:
            print('App is running successfully')
        else:
            print('App is down. Fix it')
            msg = f'App returned {response.status_code}'
            send_notification(msg)
            restart_container()
    except Exception as ex:
        print(f'Connection error happened: {ex}')
        msg = 'App Network is Down!'
        send_notification(msg)
        reboot_instance()
        time.sleep(60)
        restart_container()


schedule.every(5).seconds.do(monitor_app)

while True:
    schedule.run_pending()
