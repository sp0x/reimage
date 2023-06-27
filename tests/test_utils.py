from unittest import TestCase
from src.reimage.utils import get_extra_filename


class Test(TestCase):
    def test_get_extra_filename(self):
        new_filename = get_extra_filename("/home/vasko/go/1/a.jpg")
        new_filename_2 = get_extra_filename("/home/vasko/go/1/b.jpg")
        self.assertEqual("/home/vasko/go/1/a_1.jpg", new_filename)
        self.assertEqual("/home/vasko/go/1/b_2.jpg", new_filename_2)
