from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

import reversion

from base.model_utils import TimeStampedModel


class Area(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'

    def __unicode__(self):
        return unicode('{}'.format(self.name))

reversion.register(Area)


class ModerateState(models.Model):
    """Accept, reject or pending"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = 'Moderate'
        verbose_name_plural = 'Moderated'

    def __unicode__(self):
        return unicode('{}'.format(self.name))

    @staticmethod
    def pending():
        return ModerateState.objects.get(slug='pending')

    @staticmethod
    def published():
        return ModerateState.objects.get(slug='published')

    @staticmethod
    def rejected():
        return ModerateState.objects.get(slug='rejected')

reversion.register(ModerateState)


class Event(TimeStampedModel):
    """ Event """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True)
    area = models.ForeignKey(Area)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    moderate_state = models.ForeignKey(ModerateState)
    date_moderated = models.DateTimeField(blank=True, null=True)
    user_moderated = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='+'
    )

    class Meta:
        ordering = ['modified']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __unicode__(self):
        return unicode('{}'.format(self.title))

reversion.register(Event)


def _default_moderate_state():
    return ModerateState.pending()


class Story(TimeStampedModel):
    """News story"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True)
    area = models.ForeignKey(Area)
    title = models.CharField(max_length=100)
    description = models.TextField()
    picture = models.ImageField(upload_to='story/%Y/%m/%d', blank=True)
    moderate_state = models.ForeignKey(ModerateState, default=_default_moderate_state)
    date_moderated = models.DateTimeField(blank=True, null=True)
    user_moderated = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='+'
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'

    def __unicode__(self):
        return unicode('{}'.format(self.title))

    def save(self, *args, **kwargs):
        if self.user:
            pass
        elif self.email and self.name:
            pass
        else:
            raise ValueError(
                "Story must have a 'user' or a 'name' AND 'email'"
            )
        super(Story, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('story.detail', args=[self.pk])

    def _set_moderated(self, user):
        self.date_moderated = datetime.now()
        self.user_moderated = user

    def set_published(self, user):
        self.moderate_state = ModerateState.objects.get(slug='published')
        self._set_moderated(user)

    def set_rejected(self, user):
        self.moderate_state = ModerateState.objects.get(slug='rejected')
        self._set_moderated(user)

    def user_can_edit(self, user):
        """
        A member of staff can edit anything.  A standard user can only edit
        their own stories if they haven't been moderated
        """
        result = False
        if user.is_staff:
            result = True
        elif user.is_active and not self.date_moderated:
            result = user == self.user
        return result

    def _author(self):
        return self.name or self.user.username
    author = property(_author)

    def _published(self):
        return self.moderate_state == ModerateState.published()
    published = property(_published)

    def _rejected(self):
        return self.moderate_state == ModerateState.rejected()
    rejected = property(_rejected)

reversion.register(Story)
