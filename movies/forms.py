from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Movie, MovieScreening, MovieTicket, MovieReview, Theater

class MovieSearchForm(forms.Form):
    """Form for searching movies"""
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search movies by title, director, or cast...',
            'class': 'form-control'
        })
    )
    genre = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label="All Genres",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    rating = forms.ChoiceField(
        choices=[('', 'All Ratings')] + Movie._meta.get_field('rating').choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Genre
        self.fields['genre'].queryset = Genre.objects.all()


class MovieTicketBookingForm(forms.ModelForm):
    """Form for booking movie tickets"""
    
    class Meta:
        model = MovieTicket
        fields = ['ticket_type', 'quantity', 'email', 'phone']
        widgets = {
            'ticket_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, screening=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.screening = screening
        self.user = user
        
        # Pre-populate email if user is logged in
        if user and user.is_authenticated:
            self.fields['email'].initial = user.email
        
        # Add screening-specific validation
        if screening:
            max_quantity = min(10, screening.available_seats)
            self.fields['quantity'].widget.attrs['max'] = max_quantity
            self.fields['quantity'].validators = [
                MinValueValidator(1),
                MaxValueValidator(max_quantity)
            ]
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if self.screening and quantity > self.screening.available_seats:
            raise forms.ValidationError(
                f"Only {self.screening.available_seats} seats available."
            )
        return quantity
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Check if screening is still available
        if self.screening and self.screening.is_past:
            raise forms.ValidationError("This screening has already passed.")
        
        if self.screening and self.screening.is_sold_out:
            raise forms.ValidationError("This screening is sold out.")
        
        return cleaned_data


class MovieReviewForm(forms.ModelForm):
    """Form for movie reviews"""
    
    class Meta:
        model = MovieReview
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f"{i} Star{'s' if i != 1 else ''}") for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Share your thoughts about this movie...'
            }),
        }


class MovieForm(forms.ModelForm):
    """Form for creating/editing movies (admin use)"""
    
    class Meta:
        model = Movie
        fields = [
            'title', 'description', 'duration', 'release_date', 'director', 
            'cast', 'genres', 'language', 'country', 'rating', 
            'poster_image', 'trailer_url', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'director': forms.TextInput(attrs={'class': 'form-control'}),
            'cast': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'genres': forms.CheckboxSelectMultiple(),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'poster_image': forms.URLInput(attrs={'class': 'form-control'}),
            'trailer_url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MovieScreeningForm(forms.ModelForm):
    """Form for creating/editing movie screenings"""
    
    class Meta:
        model = MovieScreening
        fields = [
            'movie', 'theater', 'show_date', 'show_time', 
            'base_price', 'premium_price', 'total_seats'
        ]
        widgets = {
            'movie': forms.Select(attrs={'class': 'form-control'}),
            'theater': forms.Select(attrs={'class': 'form-control'}),
            'show_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'show_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'premium_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['movie'].queryset = Movie.objects.filter(is_active=True)
        self.fields['theater'].queryset = Theater.objects.filter(is_active=True)


class TheaterForm(forms.ModelForm):
    """Form for creating/editing theaters"""
    
    class Meta:
        model = Theater
        fields = ['name', 'location', 'capacity', 'facilities', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'facilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
