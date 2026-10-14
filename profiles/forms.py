from django import forms
from django.core.validators import URLValidator

from .models import INTERESTS, Profile

web_url = URLValidator(schemes=["http", "https"])


class ProfileForm(forms.ModelForm):
    interests = forms.MultipleChoiceField(choices=INTERESTS, required=False, widget=forms.CheckboxSelectMultiple,
                                          help_text="Pick what you want to learn. We use it to suggest courses.")

    class Meta:
        model = Profile
        fields = ["headline", "stage", "location", "bio", "interests", "github", "linkedin", "website"]
        labels = {"stage": "Where are you now?", "github": "GitHub", "linkedin": "LinkedIn"}
        widgets = {
            "headline": forms.TextInput(attrs={"placeholder": "Final-year CSE student"}),
            "location": forms.TextInput(attrs={"placeholder": "Chennai"}),
            "bio": forms.Textarea(attrs={"rows": 3, "placeholder": "A line or two about you and what you're working towards."}),
            "github": forms.URLInput(attrs={"placeholder": "https://github.com/you"}),
            "linkedin": forms.URLInput(attrs={"placeholder": "https://www.linkedin.com/in/you"}),
            "website": forms.URLInput(attrs={"placeholder": "https://…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["stage"].choices = [("", "Choose one")] + list(Profile.Stage.choices)
        for name in ("github", "linkedin", "website"):
            self.fields[name].validators.append(web_url)      # no javascript: or other schemes

    def clean_headline(self):
        return " ".join(self.cleaned_data["headline"].split())
