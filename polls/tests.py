import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from .models import Question, Choice


class QuestionMethodTest(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertFalse(future_question.was_published_recently())

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is older than 1 day
        """
        time = timezone.now() + datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertFalse(old_question.was_published_recently())

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for question whose
        pub_date is within the last day
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertTrue(recent_question.was_published_recently())


def create_question(question_text, days):
    """
    Creates a question with the given `question_text` published the given
    number of `days` offset of now (negative for questions published in the
    past, positive for questions to be published in the future)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionViewTests(TestCase):

    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the index
        page
        """
        create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question>']
        )

    def test_index_view_with_a_future_question(self):
        """
        Question with a pub_date in the future should not be displayed on the
        index page
        """
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_and_past_questions(self):
        """
        If past and future questions exist, only past question should be
        displayed
        """
        create_question(question_text="Past question", days=-30)
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question>']
        )

    def test_index_view_with_two_past_questions(self):
        """
        Index page should be able to display multiple questions at once
        """
        create_question(question_text="Past question 1", days=-30)
        create_question(question_text="Past question 2", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2>', '<Question: Past question 1>']
        )


class QuestionDetailTests(TestCase):

    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a future question should return error 404
        """
        future_question = create_question(
            question_text="Future question", days=5
        )
        response = self.client.get(
            reverse('polls:detail', args=(future_question.id,))
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a past question should display question text
        """
        past_question = create_question(
            question_text="Past question", days=-30
        )
        response = self.client.get(
            reverse('polls:detail', args=(past_question.id,))
        )
        self.assertContains(response, past_question.question_text,
                            status_code=200)


class QuestionResultsTests(TestCase):

    def test_results_view_with_a_future_question(self):
        """
        The results view of a future question should return error 404
        """
        future_question = create_question(
            question_text="Future question", days=5
        )
        response = self.client.get(
            reverse('polls:results', args=(future_question.id,))
        )
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_question(self):
        """
        The results view of a past question should display question text and

        """
        past_question = create_question(
            question_text="Past question", days=-30
        )
        choice_1 = Choice.objects.create(
            question=past_question,
            choice_text="Choice 1",
            votes=1
        )
        choice_2 = Choice.objects.create(
            question=past_question,
            choice_text="Choice 2",
            votes=2
        )
        response = self.client.get(
            reverse('polls:results', args=(past_question.id,))
        )
        self.assertContains(
            response,
            past_question.question_text,
            status_code=200
        )
        self.assertContains(
            response,
            "{0} -- {1} vote".format(choice_1.choice_text, choice_1.votes)
        )
        self.assertContains(
            response,
            "{0} -- {1} vote".format(choice_2.choice_text, choice_2.votes)
        )
