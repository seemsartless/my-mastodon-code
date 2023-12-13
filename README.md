# my-mastodon-code
My code for working with the Mastodon API.

## client_1_read_details.py
As simple as possible Python script to connect to a Mastodon server using an API key and reading details of recent posts by the corresponding user. No error checking, not great handling of the API key, but it gets the job done.

###   1. Read local configuration file and get API key
###   2. Connect to Mastodon server
```
    from mastodon import Mastodon
    m_object = Mastodon(access_token=m_access_token, api_base_url=m_base_url)`
```
###   3. Get details of the user associated with the token
```
    user_id=m_object.account_verify_credentials()['id']
```

###   4. Read and print details from the user associated with the token
```
    user_toots = m_object.account_statuses(id=user_id)
    for i in user_toots:
        print(f"\nUser posting:: {i['content'][:100]}")
        print(f"\tTags: {i['tags']}")
```
## client_2_read_details_w_object.py
Starting with the basic code in client_1_read_details.py, move as much as possible to a 'wrapper' Mastodon object
###   1. Read local configuration file and get API key
###   2. Create our Mastodon Wrapper object, connected to the server
```
    m = MastodonWrapper(
        base_url=m_base_url,
        access_token=m_access_token,
        time_zone=local_time_zone,
        verbose=False
    )
```
### 3. Print out the recent updates from the user associated with the token
```
    m.simple_recent()
```
### 4. Will add more methods to the wrapper object, like a calculation of how long it has been since the last post (based on time zone specified in `time_zone`)
```
    print(f"{m.hours_since_last_post()} hours since the last post.")
```

## Reference
https://mastodonpy.readthedocs.io/en/stable/index.html
