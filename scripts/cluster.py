import json
import subprocess
import os
import logging

logging.basicConfig(level="DEBUG")

def main():
    echo(os.getenv('FOLDER'))
    profiles = subprocess.getoutput('yc config profile list')
    logging.debug(f"Profiles: {profiles}")
    if not profiles or not 'otus' in profiles:
        error = 0
        error += os.system('yc config profile create otus')
        logging.debug(f"Creating profile errors: {error}")
        if not error:
            error += os.system('echo $SECRET temp_key.key')
            logging.debug(f"Adding file errors: {error}")
            error += os.system('yc config set service-account-key temp_key.key')
            logging.debug(f"Adding key errors: {error}")
            error += os.system('rm temp_key.key')
            logging.debug(f"Removing file errors: {error}")
            if not error:
                error += os.system('yc config set cloud-id $CLOUD')
                logging.debug(f"Adding cloud errors: {error}")
                error += os.system('yc set folder-id $FOLDER')
                logging.debug(f"Adding folder errors: {error}")
        if error:
            raise Exception
    clusters = json.loads(subprocess.getoutput('yc managed-kubernetes cluster list --format json'))
    logging.debug(f'{clusters}')
    cluster_exists = 0
    for cluster in clusters:
        if cluster['name'] == 'otus':
            cluster_exists = 1
            if cluster['status'] == "STOPPED":
                os.system('yc managed-kubernetes cluster start --name otus')
                logging.debug(f"Starting cluster")
    if not cluster_exists:
        creation = json.loads(subprocess.getoutput('yc managed-kubernetes cluster create --name otus --network-name otus --subnet-name otus --zone ru-central1-a --cluster-ipv4-range "172.17.0.0/16" --service-ipv4-range "172.18.0.0/16" --public-ip --format json'))
        logging.debug(f"Creation cluster:  \n {creation}")
        

def finalizer():
    os.system('yc config unset cloud-id')
    os.system('yc config unset service-account-key')

if __name__ == "__main__":

    try:
        main()
    except:
        print('Error while running script')
    finally:
        finalizer()
