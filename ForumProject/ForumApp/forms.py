from django import forms
from .models import Category, Post, Comment, User



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'description', 'icon']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-field'}),
            'content': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        }      


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password", required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Password confirmation", required=True)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Birth date', required=False)
    username = forms.CharField(label='Username', required=True)
    avatar = forms.ImageField(label='Avatar', required=False)

    class Meta:
        model = User
        fields = ("email", "username", "full_name", "birth_date", "avatar")
        
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match!')
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), 
        required=False
    )
    
    class Meta:
        model = User
        fields = ['username', 'full_name', 'birth_date', 'avatar']


