from django.db import models


class Lessons(models.Model):
	playlist = models.ForeignKey('Playlists', related_name="lessons")
	added_date = models.DateTimeField(auto_now_add=True)


class Sounds(models.Model):
	xc_id = models.IntegerField()
	species = models.ForeignKey('Species', related_name="sp")
	lessons = models.ManyToManyField('Lessons', related_name="sounds")
	fs = models.IntegerField()
	added_date = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return u'%s' % self.xc_id

	class Meta:
		ordering = ('added_date',)


class Species(models.Model):
	eng_name = models.CharField(max_length=30, null=False)
	lessons = models.ManyToManyField('Lessons', related_name="species")

	def __unicode__(self):
		return u'%s' % self.eng_name


class PlaylistTypes(models.Model):
	playlist_type = models.CharField(max_length=20)

	def __unicode__(self):
		return u'%s' % self.playlist_type


class Playlists(models.Model):
	playlist_name = models.CharField(max_length=50)
	playlist_type = models.ForeignKey('PlaylistTypes', related_name="playlist-type")
	added_date = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return u'%s - %d' % (self.playlist_name, self.playlist_type)


class Annotations(models.Model):
	sound = models.ForeignKey('Sounds', related_name="annotations")
	user = models.ForeignKey('auth.User', related_name="annotations")
	wave_onset = models.FloatField()
	wave_offset = models.FloatField()
	species = models.ForeignKey('Species', related_name="ann-species")
	added_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('added_date',)


class GroundTruth(models.Model):
	sound = models.ForeignKey('Sounds', related_name="truth")
	onset_loc = models.FloatField()
	species = models.ForeignKey('Species', related_name="truth-species")
	added_date = models.DateTimeField(auto_now_add=True)
