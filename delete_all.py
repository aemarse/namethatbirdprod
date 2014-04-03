from api.models import Sounds, Playlists, Lessons

Sounds.objects.all().delete()
Playlists.objects.all().delete()
Lessons.objects.all().delete()
