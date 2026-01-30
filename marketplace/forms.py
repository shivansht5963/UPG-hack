from django import forms
from django.core.exceptions import ValidationError
from .models import Material, WasteListing


class WasteListingForm(forms.ModelForm):
    """
    Form for creating and editing waste listings
    """
    
    class Meta:
        model = WasteListing
        fields = [
            'title',
            'description',
            'material',
            'weight',
            'grade',
            'image1',
            'image2',
            'image3',
            'image4',
            'image5',
            'video',
            'city',
            'state',
            'pincode',
            'address',
            'latitude',
            'longitude',
            'expires_at'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Industrial PET Plastic Bottles - 500kg'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Provide detailed description of the waste material, its condition, and any special notes...'
            }),
            'material': forms.Select(attrs={
                'class': 'form-select'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight in kilograms',
                'step': '0.1',
                'min': '0.1'
            }),
            'grade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'image1': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'data-preview': 'preview-1'
            }),
            'image2': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'data-preview': 'preview-2'
            }),
            'image3': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'data-preview': 'preview-3'
            }),
            'image4': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'data-preview': 'preview-4'
            }),
            'image5': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'data-preview': 'preview-5'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '6-digit pincode',
                'maxlength': '6'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full pickup address (optional)'
            }),
            'latitude': forms.HiddenInput(attrs={
                'id': 'id_latitude'
            }),
            'longitude': forms.HiddenInput(attrs={
                'id': 'id_longitude'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
        
        labels = {
            'image1': 'Image 1 (Required for Gemini Grading)',
            'image2': 'Image 2 (Recommended)',
            'image3': 'Image 3 (Recommended)',
            'image4': 'Image 4 (Recommended)',
            'image5': 'Image 5 (Recommended)',
            'video': 'Video Demonstration (Optional)',
            'expires_at': 'Listing Expiry (Optional)'
        }
        
        help_texts = {
            'weight': 'Total weight of waste material in kilograms',
            'grade': 'AI will automatically set this based on image analysis',
            'image1': 'Upload up to 5 clear photos for Gemini AI grading (at least 1 required)',
            'expires_at': 'Leave blank for no expiry'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter only active materials
        self.fields['material'].queryset = Material.objects.filter(is_active=True)
        
        # Pre-fill location from user profile
        if self.user and not self.instance.pk:
            self.fields['city'].initial = self.user.city
            self.fields['state'].initial = self.user.state
            self.fields['pincode'].initial = self.user.pincode
    
    def clean_pincode(self):
        """Validate pincode format"""
        pincode = self.cleaned_data.get('pincode')
        if not pincode.isdigit() or len(pincode) != 6:
            raise ValidationError("Please enter a valid 6-digit pincode.")
        return pincode
    
    def clean_weight(self):
        """Validate weight is positive"""
        weight = self.cleaned_data.get('weight')
        if weight <= 0:
            raise ValidationError("Weight must be greater than 0.")
        return weight
    
    def clean_image1(self):
        """Validate primary image is provided"""
        image = self.cleaned_data.get('image1')
        if not image and not self.instance.pk:
            raise ValidationError("Primary image is required for new listings.")
        return image
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        
        # Validate video size if uploaded
        video = cleaned_data.get('video')
        if video and video.size > 50 * 1024 * 1024:  # 50MB
            raise ValidationError({
                'video': 'Video file size must be less than 50MB.'
            })
        
        return cleaned_data


class MarketplaceFilterForm(forms.Form):
    """
    Form for filtering marketplace listings
    """
    
    material = forms.ModelChoiceField(
        queryset=Material.objects.filter(is_active=True),
        required=False,
        empty_label="All Materials",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    grade = forms.ChoiceField(
        choices=[('', 'All Grades')] + WasteListing.GRADE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_weight = forms.FloatField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min kg'
        })
    )
    
    max_weight = forms.FloatField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max kg'
        })
    )
    
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by city'
        })
    )
    
    state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by state'
        })
    )
    
    verified_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="Show verified listings only"
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('weight', 'Weight: Low to High'),
            ('-weight', 'Weight: High to Low'),
            ('-trust_score', 'Trust Score: High to Low'),
        ],
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class VerificationForm(forms.Form):
    """
    Form for mock OpenCV verification
    """
    
    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Upload image for AI verification"
    )
    
    material_type = forms.ModelChoiceField(
        queryset=Material.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Expected material type"
    )
