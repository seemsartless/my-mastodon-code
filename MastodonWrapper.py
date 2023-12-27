from mastodon import Mastodon
from datetime import datetime, timedelta
import pytz
import pandas as pd
import os
import time
import random
import re

class MastodonWrapper:
    def __init__(self, base_url, access_token, time_zone, ok_to_post, pause_seconds=8, verbose=False):
        self.object_state = "Unable to connect"
        self.base_url = base_url
        self.access_token = access_token
        self.time_zone = time_zone
        self.local_timezone = pytz.timezone(self.time_zone)
        self.verbose = verbose  # If set to TRUE will print out debug information
        self.ok_to_post = ok_to_post
        self.pause_seconds = pause_seconds
        self.recent_toots = False
        self.log_column_names = ["task", "details", "timestamp"]
        self.log = pd.DataFrame(columns=self.log_column_names)

        # Will use some ANSI colours - not TOO many
        self.color_reset = '\033[0m'
        self.color_error = '\033[91m'
        self.color_pass  = '\033[92m'
        self.color_quote = '\033[90m\033[3m'



        # Connect to the Mastodon server - this never seemed to return an error
        self.m_object = Mastodon(access_token=self.access_token, api_base_url=self.base_url)
        self.to_log("mastodon-connect", f"base URL: >{self.base_url}<")

        # Step 3. Get details of the user associated with the token, specifically
        # the user ID associated with the mastodon server we've connected to
        try:
            self.user_id = self.m_object.account_verify_credentials()['id']
            self.user_name = self.m_object.account_verify_credentials()['username']
            self.display_name = self.m_object.account_verify_credentials()['display_name']

        except Exception as e:
            self.object_state = f"Error 7121 connecting to {self.base_url}:\n\tAPI: {self.access_token[:3]}...{self.access_token[-3:]} \n\tMastodonError: {e}"
            print(self.object_state) if verbose else None
            return
        self.to_log("mastodon-user_name", self.user_name)
        self.to_log("mastodon-display_name", self.display_name)
        self.to_log("mastodon-user_id", self.user_id)

        if verbose:
            print("\nUser details associated with this token:")
            print(f"\t    username: {self.user_name}")
            print(f"\tdisplay_name: {self.display_name}")
            print(f"\t          id: {self.user_id}'")
        self.object_state = "Connected to server"

    def post_update(self, details, verbose=False):
        """
        Ready to post an update to the Mastodon serve, with the data in the details dictionary
        :param details: A dictionary with the details of this one update
        :param verbose: Set to TRUE to have some debug and status info printed
        :return:
        """
        include_image = False
        possible_keyboard_input = random.choice('wrpsdfghjkzvmb')
        if len(details['image_name']) > 0:
            include_image = True

            print(f"Need to upload image {details['full_image_name']}")
            if os.path.isfile(details['full_image_name']):
                self.to_log("File exists", f"Will upload the file {details['full_image_name']}")
                self.to_log("Image ALT text", details['image_text'])
                if self.__user_ok_to_post(self.ok_to_post, possible_keyboard_input, details):
                    m_image_post = self.m_object.media_post(media_file=details['full_image_name'], description=details['image_text'])
                    self.to_log("Image post results", m_image_post)
                    self.to_log("Image ID", m_image_post['id'])
                    print(f"Image was uploaded, now pausing for {self.pause_seconds} seconds before posting the update itself...")
                    time.sleep(self.pause_seconds)
                    print("... posting the status now.")
                    res = self.m_object.status_post(status=details['full_update_text'],
                                                    media_ids=m_image_post['id'],
                                                    spoiler_text=details.get('spoiler_text', None),
                                                    sensitive=details.get('sensitive', False)
                                                    )
                    self.to_log("Image status_post()", res)
                else:
                    print("Did NOT upload photo to Mastodon, but was ready to.")
                    self.to_log("Did NOT call media_post()", "Was ready to post image to Mastodon, but the variable was set to False")

            else:
                self.to_log("STOP", f"Missing file >{details['full_image_name']}<")
                print(f"\nError: cannot find the image file: >{details['full_image_name']}<")
                return
        else:
            print(f"Now create the API call we'll need using Mastodon.status_post():\n{details['full_update_text']}")
            if self.__user_ok_to_post(self.ok_to_post, possible_keyboard_input, details):
                res = self.m_object.status_post(status=details['full_update_text'],
                                                spoiler_text=details.get('spoiler_text', None),
                                                sensitive=details.get('sensitive', False)
                                                )
                self.to_log("No image status_post()", res)
            else:
                print("Did NOT post to Mastodon, but was ready to.")
                self.to_log("Did NOT call status_post()", "Was ready to post to Mastodon, but the variable was set to False")

    def time_for_next_post(self, delay, verbose=False):
        """
        Many bots have a delay between posts - this method will return the time the next
        post can be made after the delay converted to the specified timezone
        :param delay: Hours between posts
        :param verbose: Set to TRUE to have some debug and status info printed (not used here)
        :return: A datetime string
        """
        hours_since = self.hours_since_last_post()
        current_time = datetime.now(self.local_timezone)
        return current_time + timedelta(hours=(delay-hours_since))

    def hours_since_last_post(self, verbose=False):
        """Calculate the number of hours since the last Mastodon toot

        :param verbose: Set to TRUE to have some debug and status info printed
        :return: number of hours since last Mastodon toot
        """
        if not self.recent_toots:  # Don't want to read this again and again
            print(f"Call account_status() to get recent toots") if verbose else None
            self.recent_toots = self.m_object.account_statuses(id=self.user_id)

        i = self.recent_toots[0]

        post_datetime_utc = i['created_at'].astimezone(pytz.timezone('UTC'))
        local_timezone = self.local_timezone
        local_time = post_datetime_utc.astimezone(local_timezone)
        current_local_time = datetime.now(self.local_timezone)
        time_difference = current_local_time - local_time
        hours_ago = time_difference.total_seconds() / 3600

        if verbose:
            print(f"\nMost recent user posting:\n\t{i['content'][:100]}")
            print(f"\tCreated: {i['created_at']}")   # like 2023-12-11 21:12:47.197000+00:00
            print(f"\tUTC time:", post_datetime_utc)
            print(f"\t{self.time_zone} time:", local_time)
            print(f"\t{hours_ago:.2f} hours ago")
        self.to_log("mastodon-hours_since_post", hours_ago)
        return hours_ago

    def simple_recent(self, verbose=False):
        """
        Prints out the details of the most recent Mastodon toots. Nothing too sophisticated
        yet, just a demonstration of including this code in the object.
        :param verbose: Set to TRUE to have some debug and status info printed
        :return: None
        """
        if not self.recent_toots:  # Don't want to read this again and again
            print(f"Call account_status() to get recent toots") if verbose else None
            self.recent_toots = self.m_object.account_statuses(id=self.user_id)
        for i in self.recent_toots:
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

    def media_files(self, verbose=False):
        """
        List the media files already used by this user. (Does NOT include media files uploaded
        but not actually used, unfortunately.
        :param vebose: set to TRUE to have some debug and status info printed
        :return: None
        """
        if not self.recent_toots:  # Don't want to read this again and again
            print(f"Call account_status() to get recent toots") if verbose else None
            self.recent_toots = self.m_object.account_statuses(id=self.user_id)

        media_files = []
        for status in self.recent_toots:
            if 'media_attachments' in status:
                # Should do more with this than just print it, but it is a start
                media_files.extend(status['media_attachments'])
        print("Details on the media used in this user's recent updates:")
        for media in media_files:
            # For all possible fields, see https://mastodonpy.readthedocs.io/en/stable/02_return_values.html#media-dicts
            # TODO Add IF - different sorts of media have, or don't have, media['meta']['original']['size']
            print(f"ID: {media['id']} ({media['type']} {media['meta']['original']['size']} px) \n\t{media['description']} \n\tURL: {media['url']}")

    def __repr__(self):
        """
        A string representation explaining the object
        :return: String
        """
        if self.object_state == "Connected to server":
            return f"Mastodon connection to {self.base_url} associated with '@{self.user_name}' - {self.display_name} "
        else:
            return f"ERROR: {self.object_state}"

    def __user_ok_to_post(self, main_flag, key_input_chr, this_post):
        """
        Some simple logic to determine if everything is ready for posting, and if we want the code
        to as for a random key to continue.
        :param main_flag: Will be 'yes' or 'ask' or 'no'
        :param key_input_chr:
        :param this_post:
        :return:
        """
        if main_flag == 'yes':
            return True  # Post this item, don't even ask
        elif main_flag == 'ask':
            print(f"Ready to post to mastodon:\n\t{this_post['full_update_text']}\n\t{this_post['image_name']}\n\t{this_post['image_text']}\n\tMonth: {this_post['month']} / Date: {this_post['day']}")
            keypress = input(f"Enter {key_input_chr} to post to Mastodon, or 0 to cancel:   ")
            if keypress == key_input_chr:
                return True
        return False
    def to_log(self, task, details):
        """
        An internal function to add a row to the log
        :param task: Short task name
        :param details: Sentence to describe the details
        :return: None
        """
        self.log = pd.concat([self.log,
                              pd.DataFrame([[task, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]], columns=self.log_column_names)
                              ], ignore_index=True)
    def log_df(self):
        return self.log
    def save_log_to_csv(self, path_name):
        """
        Write the log dataframe to a csv file, including the current timestamp in the file name
        :param path_name: Local path for the log CSV file
        :return: None
        """
        file_name=f'MastodonWrapperLog-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.csv'
        print(f"\nWriting log file to:\n\tPath: {path_name}\nFile: \t{file_name}")
        try:
            self.log.to_csv(f'{path_name}{file_name}', index=False)
        except Exception as e:
            print(f'Unable to write log file:\n\t{path_name}{file_name}\n')
            print(self.log)
    def state(self):
        """
        A simple function to return the state of the object.
        :return: String
        """
        return self.object_state

    def already_posted(self, next_dict, verbose=False):
        """
        Return True if the posting data in next_dict has already been posted

        :param next_dict:
        :return: Boolean
        """
        if not self.recent_toots:  # Don't want to read this again and again
            print(f"Call account_status() to get recent toots") if verbose else None
            self.recent_toots = self.m_object.account_statuses(id=self.user_id)

        print(f"The next planned update text is:\n{next_dict['full_update_text']}") if verbose else None
        for status in self.recent_toots:
            temp_post = re.sub(r'<.*?>', '', status['content'])
            temp_post = re.sub(r'&#39;', "'", temp_post)
            temp_post = re.sub(r'&amp;', "&", temp_post)
            print(temp_post) if verbose else None

            if next_dict['full_update_text'] == temp_post:
                print(f"{self.color_error}Error: {self.color_reset}The next post defined has already been posted to Mastodon at {status['created_at']}:\n{self.color_quote}{temp_post}{self.color_reset}")
                self.to_log("no_new_post", f"The next planned update has already been posted at {status['created_at']}")
                self.to_log("duplicate_content", temp_post)
                return True
        # If there is no match, all is OK
        self.to_log("next_post_is_new", "The next planned update has NOT already been posted")
        return False
