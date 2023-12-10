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
## client_2_read_details.py (tbd)
With simple working code, it is time to create a simple Python object to make all of this work better.

## Reference
https://mastodonpy.readthedocs.io/en/stable/index.html
