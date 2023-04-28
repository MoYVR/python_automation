import boto3
import schedule
from operator import itemgetter

ec2_client = boto3.client('ec2', region_name='us-west-1')

snapshots = ec2_client.describe_snapshots(
    OwnerIds=['self']
)

sorted_by_date = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse=True)

def deleteing_snapshots():
    for snap in sorted_by_date[2:]:
        response = ec2_client.delete_snapshot(
            SnapshotId=snap['SnapshotId']
        )
        print(response)

schedule.every(20).seconds.do(deleteing_snapshots)

while True:
    schedule.run_pending()
