from django.test import TestCase

from .models import Poll


class PollModelTests(TestCase):

    def test_str_returns_title(self):
        poll = Poll.objects.create(
            title="Test Poll"
            )
        self.assertEqual(str(poll), "TEST POLL", "Poll.__str__() should return the title in capital")
