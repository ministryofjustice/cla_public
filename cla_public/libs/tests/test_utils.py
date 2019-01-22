import unittest

from cla_public.libs.utils import category_id_to_name


class UtilsTest(unittest.TestCase):
    def test_category_id_to_name(self):
        category_id = "clinneg"
        result = category_id_to_name(category_id)
        self.assertEquals(u"Clinical negligence", result)
