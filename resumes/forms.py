from django import forms

from .services import MAX_UPLOAD_BYTES


class ResumeForm(forms.Form):
    resume = forms.FileField(label="Your resume (PDF, up to 5 MB)",
                             widget=forms.ClearableFileInput(attrs={"accept": "application/pdf,.pdf"}))
    target_role = forms.CharField(
        label="Role you're aiming for", required=False, max_length=80,
        help_text="Optional. Helps the review check the right keywords.",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Backend Developer, Data Engineer"}))
    consent = forms.BooleanField(
        label="I agree: my resume is stored in Parottasalna's Google Drive, reviewed by an AI model on our own "
              "computer, and the report is emailed to me. The PDF is deleted a few days after the review.",
        error_messages={"required": "Please confirm, so we can review your resume."})

    def clean_resume(self):
        f = self.cleaned_data["resume"]
        if not f.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Please upload a PDF file.")
        if f.size > MAX_UPLOAD_BYTES:
            raise forms.ValidationError("That file is larger than 5 MB. Please upload a smaller PDF.")
        f.seek(0)
        if f.read(5) != b"%PDF-":     # the name says .pdf; check the content agrees
            raise forms.ValidationError("That file isn't a valid PDF.")
        f.seek(0)
        return f

    def clean_target_role(self):
        return " ".join(self.cleaned_data["target_role"].split())
