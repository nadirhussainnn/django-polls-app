from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

from .models import Poll, Question, Choice


class PollModelAndViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Create shared objects used by all tests:
        - one active poll (expires tomorrow) with one question and two choices
        - one expired poll (expired yesterday) with one question and two choices
        """
        
        today = timezone.localdate()
        
        # Active poll
        cls.active_poll = Poll.objects.create(
            title="Active Poll",
            created_at=today,
            expiry=today + timedelta(days=1),
        )

        q1 = Question.objects.create(poll=cls.active_poll, text="Active Question?")
        cls.choice_a1 = Choice.objects.create(question=q1, choice_text="A", votes=0)
        cls.choice_a2 = Choice.objects.create(question=q1, choice_text="B", votes=2)

        # Expired poll
        cls.expired_poll = Poll.objects.create(
            title="Expired Poll",
            created_at=today - timedelta(days=10),
            expiry=today - timedelta(days=1),
        )
        q2 = Question.objects.create(poll=cls.expired_poll, text="Expired Question?")
        cls.choice_e1 = Choice.objects.create(question=q2, choice_text="X", votes=5)
        cls.choice_e2 = Choice.objects.create(question=q2, choice_text="Y", votes=1)

        # Test client
        cls.client = Client()

    # 1. Model: __str__ returns title in capital
    def test_str_returns_title(self):
        self.assertEqual(str(self.active_poll), "ACTIVE POLL")

    # 2. is_expired for today's (expiry in future) should return False
    def test_is_expired_with_tomorrows_date(self):
        self.assertFalse(self.active_poll.is_expired())

    # 3. is_expired for yesterday should return True
    def test_is_expired_with_yesterdays_date(self):
        self.assertTrue(self.expired_poll.is_expired())

    # 4. is_expired for future date should still return False
    def test_is_expired_with_future_date(self):
        future = timezone.localdate() + timedelta(days=10)
        p = Poll.objects.create(title="F", created_at=timezone.localdate(), expiry=future)
        self.assertFalse(p.is_expired())

    # 5. Poll default created_at and expiry are present
    def test_poll_defaults_exist(self):
        p = Poll.objects.create(
            title="Defaults", 
            created_at=timezone.localdate(), 
            expiry=timezone.localdate() + timedelta(days=3)
            )
        self.assertIsNotNone(p.created_at)
        self.assertIsNotNone(p.expiry)

    # 6. Index view returns 200
    def test_index_view_status_code(self):
        resp = self.client.get(reverse("index"))
        self.assertEqual(resp.status_code, 200)

    # 7. Index view contains polls in context
    def test_index_view_context_contains_polls(self):
        resp = self.client.get(reverse("index"))
        self.assertIn("polls", resp.context)
        # at least the two we created
        self.assertTrue(len(resp.context["polls"]) >= 2)

    # 8. Detail view shows questions for a poll
    def test_detail_view_shows_questions(self):
        resp = self.client.get(reverse("detail", args=[self.active_poll.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Active Question?")

    # 9. Posting a valid vote increments the choice votes
    def test_vote_post_increments_choice_votes(self):
        before = self.choice_a1.votes
        resp = self.client.post(reverse("vote", args=[self.active_poll.id]), {
            "question_id": self.choice_a1.question.id,
            "choice": self.choice_a1.id
        })
        # after successful vote it should redirect (302) to results
        self.assertEqual(resp.status_code, 302)
        self.choice_a1.refresh_from_db()
        self.assertEqual(self.choice_a1.votes, before + 1)

    # 10. GET to vote should redirect to detail prevent voting via GET
    def test_vote_get_redirects_to_detail(self):
        resp = self.client.get(reverse("vote", args=[self.active_poll.id]))
        self.assertEqual(resp.status_code, 302)

        # redirect target should be detail page
        self.assertIn(reverse("detail", args=[self.active_poll.id]), resp.url)

    # 11. Results view shows votes correctly for expired poll
    def test_results_view_shows_votes(self):
        resp = self.client.get(reverse("results", args=[self.expired_poll.id]))
        self.assertEqual(resp.status_code, 200)
        # should show top choice and its votes
        self.assertContains(resp, "X")   # choice_e1 text
        self.assertContains(resp, "5")   # its votes

    # 12. Expired poll should not allow voting (POST should redirect to results)
    def test_expired_poll_blocks_vote_and_redirects_results(self):
        resp = self.client.post(reverse("vote", args=[self.expired_poll.id]), {
            "question_id": self.choice_e1.question.id,
            "choice": self.choice_e1.id
        })
        # We expect a redirect to results (server-side block)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("results", args=[self.expired_poll.id]), resp.url)

    # 13. Index template includes data-expiry attribute for countdown (UI check)
    def test_index_includes_countdown_data_attribute(self):
        resp = self.client.get(reverse("index"))
        # each poll should render an element with data-expiry I checked for substring presence
        self.assertContains(resp, 'data-expiry="')

    # 14. Integration: Full flow from detail to vote to results for active poll
    def test_integration_full_flow_vote_to_results(self):
        # GET detail
        resp_detail = self.client.get(reverse("detail", args=[self.active_poll.id]))
        self.assertEqual(resp_detail.status_code, 200)

        # POST vote
        resp_vote = self.client.post(reverse("vote", args=[self.active_poll.id]), {
            "question_id": self.choice_a1.question.id,
            "choice": self.choice_a1.id
        })
        self.assertEqual(resp_vote.status_code, 302)

        # Follow redirect to results
        resp_results = self.client.get(reverse("results", args=[self.active_poll.id]))
        self.assertEqual(resp_results.status_code, 200)

        # verify votes number displayed (choice_a1 initial 0 -> now 1)
        self.choice_a1.refresh_from_db()
        self.assertContains(resp_results, str(self.choice_a1.votes))
