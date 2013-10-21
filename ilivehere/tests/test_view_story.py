from django.core.urlresolvers import reverse

from base.tests.test_utils import PermTestCase
from ilivehere.models import Story
from ilivehere.tests.scenario import (
    default_scenario_ilivehere,
    get_area_hatherleigh,
    get_story_craft_fair,
    get_story_market_fire,
)
from login.tests.scenario import (
    default_scenario_login,
    user_contractor,
)


class TestViewStory(PermTestCase):

    def setUp(self):
        default_scenario_login()
        user_contractor()
        default_scenario_ilivehere()

    def test_create_anon(self):
        self.assert_any(reverse('ilivehere.story.create.anon'))

    def test_create_anon_post(self):
        url = reverse('ilivehere.story.create.anon')
        data = dict(
            name='Patrick',
            email='code@pkimber.net',
            area=get_area_hatherleigh().pk,
            title='Chilli Night',
            description='Hot, hot, hot...',
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        Story.objects.get(name='Patrick')

    def test_create_trust_perm(self):
        self.assert_logged_in(reverse('ilivehere.story.create.trust'))

    def test_detail_perm(self):
        """the 'assert_logged_in' method uses the 'web' user"""
        story = get_story_market_fire()
        self.assert_logged_in(
            reverse('ilivehere.story.detail', kwargs={'pk': story.pk})
        )

    def test_list_perm(self):
        self.assert_logged_in(reverse('ilivehere.story.list'))

    def test_moderate_perm(self):
        story = get_story_craft_fair()
        self.assert_staff_only(
            reverse('ilivehere.story.moderate', kwargs={'pk': story.pk})
        )

    def test_update_perm(self):
        story = get_story_market_fire()
        self.assert_logged_in(
            reverse('ilivehere.story.update', kwargs={'pk': story.pk})
        )
