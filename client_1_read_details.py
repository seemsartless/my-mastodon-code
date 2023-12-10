import csv  # https://docs.python.org/3/library/csv.html
from mastodon import Mastodon

# Simple Mastodon client Python script to:
#
#   1. Read local configuration file and get API key
#   2. Connect to Mastodon server
#   3. Get details of the user associated with the token
#   4. Read and print details from the user associated with the token
#

# Step 1. Read local configuration file and get API key
with open("mastodon-private-metadata.csv", "r") as infile:
    mpm = csv.DictReader(infile, fieldnames=("variable_name", "set_to"))
    for row in mpm:  # Iterate through the rows to find the variables we need
        if row['variable_name'] == 'mastodon-base-url':
            m_base_url = row['set_to']
        if row['variable_name'] == 'access-token':
            m_access_token = row['set_to']
print("Variables read from local CSV configuration file:")
print(f"    m_base_url: {m_base_url}")
print(f"m_access_token: {m_access_token[:3]}...{m_access_token[-3:]}")

# Step 2. Connect to Mastodon server and create the Mastodon object using the details we read
m_object = Mastodon(access_token=m_access_token, api_base_url=m_base_url)

# Step 3. Get details of the user associated with the token, specifically
# the user ID associated with the mastodon server we've connected to
user_id=m_object.account_verify_credentials()['id']
print("\nUser details associated with this token:")
print(f"\t    username: {m_object.account_verify_credentials()['username']}")
print(f"\tdisplay_name: {m_object.account_verify_credentials()['display_name']}")
print(f"\t          id: {user_id}'")

# Step 4. Read and print details from the user associated with the token
user_toots = m_object.account_statuses(id=user_id)
for i in user_toots:
    # See https://mastodonpy.readthedocs.io/en/stable/02_return_values.html#toot-status-dicts for all returned values in the dictionary
    if not i['reblog']:  # An original post by this user
        print(f"\nUser posting:: {i['content'][:100]}")
        print(f"\tVisibility: {i['visibility']}")
        print(f"\tCreated: {i['created_at']}")
        print(f"\tTags: {i['tags']}")
        print(f"\tMedia: {i['media_attachments']}")
        print(f"\tMentions: {i['mentions']}")
        print(f"\turl: {i['url']}")
    else:
        print("\nA reblog by the user:")
        print(f"\tContent: {i['reblog']['content'][:100]}")
        print(f"\tCreated at: {i['reblog']['created_at']}")
        print(f"\tReblog details: {i['reblog']}")
        print(f"\tVisibility: {i['visibility']}")

# Done, short and simple