import csv  # https://docs.python.org/3/library/csv.html
from MastodonWrapper import *
from DataForUpdates import *
# from datetime import datetime, timedelta
# import pytz
# Third client file - actually make a post
#

show_verbose_details = False
post_if_all_ok = "ask"  # no | yes | ask

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
        if row['variable_name'] == 'csv-file-location':
            csv_file_location = row['set_to']
        if row['variable_name'] == 'image-file-location':
            image_file_location = row['set_to']
if show_verbose_details:
    print("Variables read from local CSV configuration file:")
    print(f"         m_base_url: {m_base_url}")
    print(f"     m_access_token: {m_access_token[:3]}...{m_access_token[-3:]}")
    print(f"    local_time_zone: {local_time_zone}")
    print(f"   post_limit_hours: {post_limit_hours}")


# Get the details on the next update we can make now
# u.update_data() will contain the Python dictionary of values we'll need to
# pass to the MastodonWrapper to make the update
u = DataForUpdates(
    csv_file='tbd',
    image_folder=image_file_location,
    include_calc_url=True,  # False if we don't want to calculate URL added today
    verbose=show_verbose_details
)

# Step 2. Create our Mastodon Wrapper object, connected to the server
m = MastodonWrapper(
    base_url=m_base_url,
    access_token=m_access_token,
    time_zone=local_time_zone,
    ok_to_post=post_if_all_ok,
    verbose=show_verbose_details
)
if m.state() != "Connected to server":
    print(f"\n*** Unable to continue ***\n{m.state()}")
    m.to_log("Unable to continue", m.state())
    exit(-321)

ready_to_post = True
# Do we have a new posting?
if m.already_posted(u.next_posting(), verbose=show_verbose_details) == True:
    ready_to_post = False
if m.hours_since_last_post() < post_limit_hours:
    print(f"Warning: It has only been been {m.hours_since_last_post()} hours since the last post, which is less than the {post_limit_hours} minimum")
    print(f"Try again at {m.time_for_next_post(delay=post_limit_hours)}")
    m.to_log("Update rate exceeded", f"Update NOT made: It has only been been {m.hours_since_last_post()} hours since the last post, which is less than the {post_limit_hours} minimum")
    ready_to_post = False

if ready_to_post:
    m.to_log("Frequency OK", f"It has been been {m.hours_since_last_post()} hours since the last post, which is more than the {post_limit_hours} minimum") if show_verbose_details else None
    m.post_update(details=u.return_dict, verbose=show_verbose_details)


# Write this log to the csv file defined in csv_file_location
m.save_log_to_csv(path_name=csv_file_location)
print(m.log_df()) if show_verbose_details else None
