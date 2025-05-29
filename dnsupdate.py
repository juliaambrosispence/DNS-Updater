# Filename: dnsupdate.py
# Desc: A DNS Updater Script for Dynamic IPs
# Date: May 29th 2025
# by Julia Spence

from dotenv import load_dotenv
import os
from cloudflare import Cloudflare
import requests

def find_ip():
    """Retrieve public IP address from http request"""
    # Get our public IP
    ip_response = requests.get("https://ipinfo.io/ip")
    if ip_response.status_code == 200:
        print("Public IP address:", ip_response.text)
    else:
        exit("Public IP address not found.")
    return ip_response.text

def retrieve_record():
    """Create cloudflare client and dns record objects for API calls"""
    # Create cloudflare client object
    client = Cloudflare(
        api_email = os.getenv("CLOUDFLARE_EMAIL"),
        api_key = os.environ.get("CLOUDFLARE_API_KEY")
    )

    # Retrieve dns records
    try:
        dns_record = client.dns.records.list(
            zone_id = os.environ.get("DNS_ZONE_ID")
        )
    except ValueError:
        exit("DNS record not found.")
    return client, dns_record

def main():
    print("DNS Updater Script ===")

    # Load environment variables
    load_dotenv()

    # Get our public IP
    ip_new = find_ip()

    cloudflare_client, cloudflare_dns_record = retrieve_record()


    # Now go through each record and see if it needs updating, if so add
    # its id to a list
    mismatched = []
    old_ip = ""
    print("DNS Records Retrieved:")
    for record in cloudflare_dns_record:
        # Print entry
        print(f"{type(record).__name__}\t{record.name}:\n\t id={record.id},\n\t content={record.content}")

        # Check if content contains old ip, if so add to mismatched
        if record.content.find(ip_new) == -1:
            # Record the old IP from the A record if it mismatches current IP
            if type(record).__name__ == "A":
                old_ip = record.content
                mismatched.append(record)
            elif record.content.find(old_ip) == -1:
                # If it's not an A type record, check if it contains the old_ip
                # Only add to mismatched records if we find the old ip
                mismatched.append(record)

    # We only update and list records if we have some
    if len(mismatched) > 0:
        print(f"Number of mismatched records: {len(mismatched)}")

        # If we couldn't find a consistently defined old IP in the A records
        # then we have a problem
        if old_ip == "":
            exit("Could not identify old IP from A records.")

        print("Updating DNS Records:")
        # Now loop through just the mismatched
        for record in mismatched:
            # For each record, replace this old IP with next
            new_cont = record.content.replace(old_ip, ip_new)
            # Replace the record with new content
            try:
                cloudflare_client.dns.records.edit(
                    dns_record_id=record.id,
                    zone_id=os.environ.get("DNS_ZONE_ID"),
                    content=new_cont
                )
                print(f"{type(record).__name__}\t{record.name}:\n\t id={record.id},\n\t content={record.content}")
            except ValueError:
                exit("Exception occurred, DNS record update failed.")
    else:
        print("DNS Record up to date!")

    print("All done! ===")

main()