from mastodon import Mastodon
from datetime import datetime
import pytz

class MastodonWrapper:
    def __init__(self, base_url, access_token, time_zone, verbose=False):
        self.object_state = "Unable to connect"
        self.base_url = base_url
        self.access_token = access_token
        self.time_zone = time_zone
        self.local_timezone = pytz.timezone(self.time_zone)
        self.verbose = verbose  # If set to TRUE will print out debug information
        self.recent_toots = False

        # Connect to the Mastodon server - this never seemed to return an error
        self.m_object = Mastodon(access_token=self.access_token, api_base_url=self.base_url)

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

        if verbose:
            print("\nUser details associated with this token:")
            print(f"\t    username: {self.user_name}")
            print(f"\tdisplay_name: {self.display_name}")
            print(f"\t          id: {self.user_id}'")
        self.object_state = "Connected to server"

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

        return hours_ago

    def simple_recent(self, verbose=False):
        """
        Prints out the details of the most recent Mastodon toots. Nothing too sophisticated
        yet, just a demonstration of including this code in the object.
        :param verbose:
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

    def state(self):
        """
        A simple function to return the state of the object.
        :return: String
        """
        return self.object_state


