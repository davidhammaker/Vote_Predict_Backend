from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from vp_app.models import Question, Answer, Reply


date_today = timezone.now()
date_yesterday = date_today - timedelta(days=1)
date_two_days_ago = date_today - timedelta(days=2)
date_tomorrow = date_today + timedelta(days=1)
date_day_after_tomorrow = date_today + timedelta(days=2)


class QuestionRepliesTests(APITestCase):
    url = reverse('question-replies', args=[1])
    url_concluded_question = reverse('question-replies', args=[3])
    url_unpublished_question = reverse('question-replies', args=[4])

    def setUp(self) -> None:
        question_1 = Question.objects.create(
            content='question 1',
            date_published=date_two_days_ago,
            date_concluded=date_tomorrow
        )
        Answer.objects.create(
            content='answer 1',
            question=question_1
        )
        Answer.objects.create(
            content='answer 2',
            question=question_1
        )
        question_2 = Question.objects.create(
            content='question 2',
            date_published=date_two_days_ago,
            date_concluded=date_tomorrow
        )
        Answer.objects.create(
            content='answer 3',
            question=question_2
        )
        Answer.objects.create(
            content='answer 4',
            question=question_2
        )

        # Concluded Question
        question_3 = Question.objects.create(
            content='question 3',
            date_published=date_two_days_ago,
            date_concluded=date_yesterday
        )
        Answer.objects.create(
            content='answer 5',
            question=question_3
        )
        Answer.objects.create(
            content='answer 6',
            question=question_3
        )

        # Unpublished Question
        question_4 = Question.objects.create(
            content='question 4',
            date_published=date_tomorrow,
            date_concluded=date_day_after_tomorrow
        )
        Answer.objects.create(
            content='answer 7',
            question=question_4
        )
        Answer.objects.create(
            content='answer 8',
            question=question_4
        )

        User.objects.create_user(username='test_user_1')
        User.objects.create_user(username='test_user_2')

    def test_no_replies(self):
        """
        If no Replies have been created, the API should return an
        empty list.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_replies(self):
        """
        If any Replies exist for the, the API should list them (and no
        others).
        """
        question_1 = Question.objects.get(id=1)
        question_2 = Question.objects.get(id=2)
        answer_1 = Answer.objects.get(id=1)
        answer_2 = Answer.objects.get(id=2)
        answer_3 = Answer.objects.get(id=3)
        answer_4 = Answer.objects.get(id=4)
        user_1 = User.objects.get(id=1)
        user_2 = User.objects.get(id=2)
        Reply.objects.create(
            user=user_1,
            question=question_1,
            vote=answer_1,
            prediction=answer_2
        )
        Reply.objects.create(
            user=user_2,
            question=question_1,
            vote=answer_2,
            prediction=answer_1
        )
        # Reply that should not show up:
        Reply.objects.create(
            user=user_1,
            question=question_2,
            vote=answer_3,
            prediction=answer_4
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [
            {
                'id': 1,
                'user': 1,
                'question': 1,
                'vote': 1,
                'prediction': 2
            },
            {
                'id': 2,
                'user': 2,
                'question': 1,
                'vote': 2,
                'prediction': 1
            }
        ])

    def test_new_reply(self):
        """
        Users can create new Replies.
        """
        user = User.objects.get(id=1)
        self.client.force_authenticate(user=user)
        data = {'vote': 1, 'prediction': 2}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {
            'id': 1,
            'user': 1,
            'question': 1,
            'vote': 1,
            'prediction': 2
        })

    def test_anonymous_reply(self):
        """
        Anonymous users cannot create new Replies.
        """
        data = {'vote': 1, 'prediction': 2}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 401)

    def test_multiple_replies(self):
        """
        Users cannot send more than one Reply per Question.
        """
        user = User.objects.get(id=1)
        self.client.force_authenticate(user=user)
        data = {'vote': 1, 'prediction': 2}
        response_1 = self.client.post(self.url, data)
        self.assertEqual(response_1.status_code, 201)
        self.assertEqual(response_1.data, {
            'id': 1,
            'user': 1,
            'question': 1,
            'vote': 1,
            'prediction': 2
        })
        data = {'vote': 1, 'prediction': 1}
        response_2 = self.client.post(self.url, data)
        self.assertEqual(response_2.status_code, 400)

    def test_multiple_users_replies(self):
        """
        Multiple Users may create Replies to a single Question
        """
        user_1 = User.objects.get(id=1)
        self.client.force_authenticate(user=user_1)
        data = {'vote': 1, 'prediction': 2}
        response_1 = self.client.post(self.url, data)
        self.assertEqual(response_1.status_code, 201)
        self.assertEqual(response_1.data, {
            'id': 1,
            'user': 1,
            'question': 1,
            'vote': 1,
            'prediction': 2
        })
        self.client.logout()
        user_2 = User.objects.get(id=2)
        self.client.force_authenticate(user=user_2)
        data = {'vote': 2, 'prediction': 1}
        response_2 = self.client.post(self.url, data)
        self.assertEqual(response_2.status_code, 201)
        self.assertEqual(response_2.data, {
            'id': 2,
            'user': 2,
            'question': 1,
            'vote': 2,
            'prediction': 1
        })

    def test_invalid_vote(self):
        """
        User votes must correspond to an Answer to the Question.
        """
        user = User.objects.get(id=1)
        self.client.force_authenticate(user=user)
        data = {'vote': 3, 'prediction': 2}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid vote.', str(response.data))

    def test_invalid_prediction(self):
        """
        User predictions must correspond to an Answer to the Question.
        """
        user = User.objects.get(id=1)
        self.client.force_authenticate(user=user)
        data = {'vote': 1, 'prediction': 3}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid prediction.', str(response.data))

    def test_new_reply_after_conclusion(self):
        """
        Users cannot create new Replies after a Question concludes.
        """
        user = User.objects.get(id=1)
        self.client.force_authenticate(user=user)
        data = {'vote': 5, 'prediction': 6}
        response = self.client.post(self.url_concluded_question, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('question has concluded', str(response.data))

    def test_get_reply_unpublished_conclusion(self):
        """
        Users cannot get Replies to an unpublished Question.
        """
        user = User.objects.get(id=1)
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url_unpublished_question)
        self.assertEqual(response.status_code, 404)

    def test_staff_get_reply_unpublished_conclusion(self):
        """
        Staff Users cannot get Replies to an unpublished Question.
        """
        user = User.objects.create_user(username='staff_user')
        user.is_staff = True
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url_unpublished_question)
        self.assertEqual(response.status_code, 200)
