import yaml


class Config(object):
    """
    Provides access to application configuration parameters stored in config yaml file.
    """

    config_filepath = None
    __config = None
    __meta = None
    __instance = None

    def __new__(cls):
        """
        Singleton. Get instance of this class. Create if not already created.
        :return:
        """
        if cls.__instance is None:
            cls.__instance = super(Config, cls).__new__(cls)
        return cls.__instance

    def load(self, path, meta=None):
        """
        Loads the applications config file
        :param path: Path to config file
        :param meta: Path to metadata file. Metadata is optional information about a setting that can be used for
            settings gui and can include labels and help text.
        :return:
        """
        with open(path, 'r') as yamlfile:
            self.__config = yaml.safe_load(yamlfile)

        if meta is not None:
            with open(meta, 'r') as metafile:
                self.__meta = yaml.safe_load(metafile)

        # Store path so that we can save later
        self.config_filepath = path

    def save(self):
        """
        Saves config file
        :return:
        """

        with open(self.config_filepath, 'w') as file:
            file.write("---\n")
            yaml.dump(self.__config, file, sort_keys=False)
            file.write("...")

    def get(self, path):
        """
        Gets a config property value.
        :param path: path to property. Path separated by .
        :return: property value
        """

        elements = path.split('.')
        last = None

        for element in elements:
            if last is None:
                if element in self.__config:
                    last = self.__config[element]
                else:
                    last = None
            else:
                if element in last:
                    last = last[element]
                else:
                    last = None

        return last

    def get_root_nodes(self):
        """
        Returns all root notes as a list
        :return: dict of root notes of YAML config file
        """
        nodes = []
        for key in self.__config:
            nodes.append(key)

        return nodes

    def set(self, path, value):
        """
        Sets a config property value. Only sets if property already exists.
        :param path: path to property. Path separated by .
        :param value: Value to set property to
        :return:
        """

        # does path exist
        if self.get(path) is not None:
            obj = self.__config
            key_list = path.split(".")

            for k in key_list[:-1]:
                obj = obj[k]

            obj[key_list[-1]] = value

    def get_meta(self, path, metakey):
        """
        Gets the metadata for a config property if specified metakey is available in metadata. If not specified or
            no metadata is available then returns None
        :param path: path to property. Path separated by.
        :param metakey: key for metadata.

        :return: property metadata for metakey
        """

        path += f'.{metakey}'
        elements = path.split('.')
        last = None

        if self.__meta is not None:
            for element in elements:
                if last is None:
                    if element in self.__meta:
                        last = self.__meta[element]
                    else:
                        last = None
                else:
                    if element in last:
                        last = last[element]
                    else:
                        last = None

        return last
