# DNS Updater Script
# by Julia Spence
# May 29th 2025

from dotenv import load_dotenv
import os
from cloudflare import Cloudflare
import requests

# Load environment variables
load_dotenv()

# Get our public IP
ip = requests.get("https://ipinfo.io/ip")
if ip.status_code == 200:
    print("Public IP address:", ip.text)
else:
    exit("Public IP address not found.")

# Create cloudflare client object
client = Cloudflare(
    api_email=os.getenv("CLOUDFLARE_EMAIL"),
    api_key=os.environ.get("CLOUDFLARE_API_KEY")
)

# Retrieve dns records
try:
    dns_record = client.dns.records.list(
        zone_id=os.environ.get("DNS_ZONE_ID")
    )
except ValueError:
    exit("DNS record not found.")

# Now go through each record and see if it needs updating, if so add
# its id to a list
mismatched_ids = []
for record in dns_record:
    print(f"{record.name}, id={record.id}, content={record.content}")

