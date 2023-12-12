import csv  # https://docs.python.org/3/library/csv.html
from MastodonWrapper import *

# Second simple Mastodon client Python script to use an object to:
#
#   1. Read local configuration file and get API key
#   2. Create a MastodonWrapper object to connect to the Mastodon server
#   3. Once again read and print details from the user associated with the token
#      but move that code into the object
#   4. Get the time since the last update from the object
#

# Step 1. Read local configuration file and get API key
with open("mastodon-private-metadata.csv", "r") as infile:
    mpm = csv.DictReader(infile, fieldnames=("variable_name", "set_to"))
    for row in mpm:  # Iterate through the rows to find the variables we need
        if row['variable_name'] == 'mastodon-base-url':
            m_base_url = row['set_to']
        if row['variable_name'] == 'access-token':
            m_access_token = row['set_to']
        if row['variable_name']  == 'local-timezone':
            local_time_zone = row['set_to']
        if row['variable_name'] == 'post-limit-hours':
            post_limit_hours = float(row['set_to'])

print("Variables read from local CSV configuration file:")
print(f"         m_base_url: {m_base_url}")
print(f"     m_access_token: {m_access_token[:3]}...{m_access_token[-3:]}")
print(f"    local_time_zone: {local_time_zone}")
print(f"   post_limit_hours: {post_limit_hours}")


# Step 2. Create our Mastodon Wrapper object, connected to the server
m = MastodonWrapper(
    base_url=m_base_url,
    access_token=m_access_token,
    time_zone=local_time_zone,
    verbose=False
)
if m.state() != "Connected to server":
    print(f"\n*** Unable to continue ***\n{m.state()}")
    exit(-321)

# All good, print out object details
print(m)

# Step 3. As with client_1_read_details.py - print the most recent updates by the owner of this API key
m.simple_recent(verbose=True)

# Will add more logic to the Mastodon wrapper object - one example:
# Step 4. Want to ensure we don't post too often, based on the server limit
hours_since_last_post = m.hours_since_last_post()

if hours_since_last_post > post_limit_hours:
    print(f"It has been {hours_since_last_post} hours since last post, which is more than the {post_limit_hours} minimum")
else:
    print(f"Warning: It has only been been {hours_since_last_post} hours since the last post, which is less than the {post_limit_hours} minimum")