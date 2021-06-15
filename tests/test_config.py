import unittest
import wxconfig as cgf


class TestConfig(unittest.TestCase):
    def test_load_and_get(self):
        config = cgf.Config()
        config.load("testconfig.yaml")
        val121 = config.get('test1.test1_2.val1_2_1')
        self.assertEqual(val121, 'val1_2_1', "Get returned incorrect value.")

    def test_set_and_save(self):
        config = cgf.Config()
        config.load("testconfig.yaml")

        path = 'test1.test1_2.val1_2_1'

        # Save new value, storing orig so we can restore later
        orig_value = config.get(path)
        config.set(path, "newval")
        config.save()

        # Reopen config and get value to see if it is previously saved value
        config = cgf.Config()
        config.load("testconfig.yaml")
        saved_value = config.get(path)
        self.assertEqual(saved_value, 'newval', "New value was not saved and returned.")

        # Restore and save file
        config.set(path, orig_value)
        config.save()

    def test_get_root_nodes(self):
        config = cgf.Config()
        config.load("testconfig.yaml")

        # Get root nodes
        root_nodes = config.get_root_nodes()

        # There should be 2
        self.assertTrue(len(root_nodes) == 2, "There should be 2 root nodes.")

        # The first should be test1 and the second should be test2
        self.assertEqual(root_nodes[0], 'test1', "First root node should be 'test1'.")
        self.assertEqual(root_nodes[1], 'test2', "Second root node should be 'test2'.")

    def test_meta(self):
        config = cgf.Config()
        config.load("testconfig.yaml", meta='testconfigmeta.yaml')

        # There should be a label and help text defined for leaf node val_1_1_1
        label = config.get_meta('test1.test1_1.val1_1_1', '__label')
        helptext = config.get_meta('test1.test1_1.val1_1_1', '__helptext')

        self.assertEqual(label, 'val 1.1.1')
        self.assertEqual(helptext, 'Value 1.1.1 Leaf')

        # There should be a label and help text for branch node test1_1
        label = config.get_meta('test1.test1_1', '__label')
        helptext = config.get_meta('test1.test1_1', '__helptext')

        self.assertEqual(label, 'Test 1.1')
        self.assertEqual(helptext, 'Test 1.1 Branch')

        # There shouldn't be a label or helptext for branch Test 1.2. These should return None
        label = config.get_meta('test1.test1_2', '__label')
        helptext = config.get_meta('test1.test1_2', '__helptext')

        self.assertTrue(label is None)
        self.assertTrue(helptext is None)

        # There shouldn't be label or helptext for leaf val_2_1_1. These should return None
        label = config.get_meta('test1.test2_1.val2_1_1', '__label')
        helptext = config.get_meta('test1.test2_1.val2_1_1', '__helptext')

        self.assertTrue(label is None)
        self.assertTrue(helptext is None)


if __name__ == '__main__':
    unittest.main()
