class DataForUpdates:
    def __init__(self, csv_file, image_folder, include_calc_url=True, max_len=500, max_image_text=1500, verbose=False):
        self.object_state = "Unable to access data"
        self.csv_input_file = csv_file
        self.image_folder = image_folder
        self.verbose = verbose
        self.max_len = max_len
        self.max_image_text = max_image_text

        #TODO Read and process the input csv file

        # For development, will hardcode the data that will be returned,
        # eventually this is read from the CSV file and processed
        self.return_dict = {
            'month': 12,
            'day': 28,
            'image_name': 'month-12-day-28-s0372_ss0072_it1006.jpeg',
            'image_text': 'A black and white photo of a large piece of machinery with the brand name De Laval on a plaque.',
            'tags': '#OTD, #Toronto #torontophoto #BWPhotography #HistoricPhoto #machinery #pump',
            'post_text': "A 26 M.G. DeLaval turbine pump in the Toronto High Level pumping station in the Republic of Rathnelly - 98 years ago today, on December 28th, 1925.",
            'spoiler_text': None,  # Set to None normally, or some teaser text for 'show more'
            'sensitive': False  # Set to False normally, or True to hide the image by default

        }
        self.object_state = "Data ready"

        # Calculate the URL - specific to this example
        if include_calc_url:
            self.return_dict['url'] = f"https://wholemap.com/historic/toronto.php?month={self.return_dict['month']}&day={self.return_dict['day']}"
        else:
            self.return_dict['url'] = ''
        # Some clean up
        # Ensure the list of tags all start with a hashtag
        if 'tags' in self.return_dict:
            tag_string = self.return_dict['tags']
            tag_string_no_commas = tag_string.replace(',', '')  # Remove commas
            tags_fixed = ' '.join(['#' + tag if not tag.startswith('#') else tag for tag in tag_string_no_commas.split()])
            if tag_string != tags_fixed:
                self.return_dict['tags'] = tags_fixed
                print(f"Added one or more '#' or removed commas in the list of tags, now:\n\t{self.return_dict['tags']}") if verbose else None

        self.return_dict['full_update_text'] = f"{self.return_dict['post_text']} {self.return_dict.get('tags', '')} {self.return_dict.get('url', '')}"
        self.return_dict['full_update_len'] = len(self.return_dict['full_update_text'])
        self.return_dict['image_text_len'] = len(self.return_dict['image_text'])

        # Add the folder to the file name
        self.return_dict['full_image_name'] = f"{self.image_folder}{self.return_dict['image_name']}"

        if verbose:
            print("One set of data has been loaded:")
            for key, value in self.return_dict.items():
                print(f"{key: >12}: {value}")
        if self.return_dict['full_update_len'] > self.max_len:
            print(f"WARNING 8812: The full post text w/ tags and URL is {self.return_dict['full_update_len']} characters which is > {self.max_len}")
            self.object_state = f"Warning 8812: The full post text w/ tags and URL is {self.return_dict['full_update_len']} characters which is > {self.max_len}"
        else:
            print(f"\nPass: The full post text w/ tags and URL is {self.return_dict['full_update_len']} characters which is < {self.max_len}") if self.verbose else None

        if len(self.return_dict['image_text']) > self.max_image_text:
            print(f"WARNING 3144: The image alt text is {len(self.return_dict['image_text'])} characters which is > {self.max_image_text}")
            self.object_state = f"Warning 3144: The image alt text is {self.return_dict['full-update-len']} characters which is > {self.max_image_text}"
        else:
            print(f"\nPass: The image alt text is {len(self.return_dict['image_text'])} characters which is < {self.max_image_text}") if self.verbose else None


    def next_posting(self):
        return self.return_dict

    def __repr__(self):
        """
        A string representation explaining the object
        :return: String
        """
        if self.object_state == "Data ready":
            return f"Data for a posting to Mastodon has been read from {self.csv_input_file} "
        else:
            return f"ERROR: {self.object_state}"

    def state(self):
        """
        A simple function to return the state of the object.
        :return: String
        """
        return self.object_state


