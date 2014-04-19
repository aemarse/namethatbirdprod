from api.models import Sounds, Playlists, Lessons, Species

Sounds.objects.all().delete()
Playlists.objects.all().delete()
Lessons.objects.all().delete()
Species.objects.all().delete()
