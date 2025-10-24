from django.db import models

class Movie(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255)
    poster = models.ImageField(upload_to='posters/')
    duration = models.CharField(max_length=20)
    language = models.CharField(max_length=50)
    genre = models.CharField(max_length=100, default="Unknown")
    rating = models.CharField(max_length=10, default="NR")

    def __str__(self):
        return self.title

class Theatre(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    meta = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre,on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return f"{self.movie.title} at {self.time} on {self.date}"

class Seat(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='seats')
    row = models.CharField(max_length=1)
    number = models.PositiveIntegerField()
    seat_type = models.CharField(max_length=20)
    price = models.PositiveIntegerField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.row}{self.number} ({'Booked' if self.is_booked else 'Available'})"

class Ticket(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seats = models.CharField(max_length=200)  # e.g. "A1,A2,A3"
    total_price = models.PositiveIntegerField()
    booking_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket for {self.showtime.movie.title} ({self.seats})"