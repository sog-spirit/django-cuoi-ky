from django.views import generic
from .models import Post, Comment
from .forms import CommentForm, PostForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import re
from django.utils.text import slugify
from django.contrib import messages

# Create your views here.
class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'index.html'
    paginate_by = 5

# class PostDetail(generic.DetailView):
#     model = Post
#     template_name = 'post_detail.html'

def user_detail(request):
    template_name = 'user_detail.html'
    context = {}
    if request.user.is_authenticated:
        context['username'] = request.user.username
        context['date_joined'] = request.user.date_joined
        context['number_of_posts'] = Post.objects.filter(status=1, author=request.user).count()

        number_of_commented = 0
        number_of_comments = 0
        all_posts = Post.objects.all()
        for post in all_posts:
            number_of_comments += post.comments.filter(name=request.user.username).count()
            number_of_commented += post.comments.exclude(name=request.user.username).count()
        context['number_of_comments'] = number_of_comments
        context['number_of_commented'] = number_of_commented

    return render(request, template_name, context)

def post_detail(request, slug):
    template_name = 'post_detail.html'
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        # comment_form = CommentForm(data=request.POST)
        comment_content = request.POST['comment']
        new_comment = Comment.objects.create(post=post, name=request.user.username, body=comment_content, active=True)
        new_comment.save()
        return redirect('post_detail', slug=post.slug)
        
    # else:
        # comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        # 'new_comment': new_comment,
    }
    return render(request, template_name, context)

def edit_detail(request, slug):
    context = {}
    template_name = 'edit_detail.html'
    post = get_object_or_404(Post, slug=slug)

    if request.method == 'POST':
        edit_form = PostForm(data=request.POST, instance=post)
        if edit_form.is_valid():
            edit_form.save()
            # return redirect('edit_detail', slug)
            context['notification'] = 'Cập nhật thành công'
    else:
        edit_form = PostForm(instance=post)
    context['edit_form'] = edit_form
    return render(request, template_name, context)

def login_form(request):
    context = {}
    return render(request, 'login.html', context)

def login_authenticate(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            login_data = request.POST.dict()
            username = login_data.get('username')
            password = login_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Sai tên tài khoản hoặc mật khẩu')
                return redirect('login_form')
        else:
            return redirect('login_form')

def logout_user(request):
    logout(request)
    return redirect('home')
    
def register_form(request):
    context = {}
    template_name = 'register.html'
    return render(request, template_name, context)

def create_user(request):
    context = {}
    template_name = 'notification.html'
    if request.method == 'POST':
        register_data = request.POST.dict()
        username = register_data.get('username')
        password = register_data.get('password')
        if User.objects.filter(username=username).exists():
            context['notification'] = 'Tên người dùng đã tồn tại'
        else:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            context['notification'] = 'Tạo tài khoản thành công'
    else:
        context['notification'] = 'Phương thức truyền không phải là phương thức POST'
    return render(request, template_name, context)

class PostedList(generic.ListView):
    template_name = 'post_list.html'
    paginate_by = 3
    def get_queryset(self):
        queryset = Post.objects.filter(status=1, author=self.request.user).order_by('-created_on')
        return queryset

class DraftList(generic.ListView):
    template_name = 'draft_list.html'
    paginate_by = 3
    def get_queryset(self):
        queryset = Post.objects.filter(status=0, author=self.request.user).order_by('-created_on')
        return queryset

def remove_accent(string):
    """
    To remove Vietnamese accent
    """
    string = re.sub('[áàảãạăắằẳẵặâấầẩẫậ]', 'a', string)
    string = re.sub('[ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ]', 'A', string)
    string = re.sub('[éèẻẽẹêếềểễệ]', 'e', string)
    string = re.sub('[ÉÈẺẼẸÊẾỀỂỄỆ]', 'E', string)
    string = re.sub('[óòỏõọôốồổỗộơớờởỡợ]', 'o', string)
    string = re.sub('[ÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ]', 'O', string)
    string = re.sub('[íìỉĩị]', 'i', string)
    string = re.sub('[ÍÌỈĨỊ]', 'I', string)
    string = re.sub('[úùủũụưứừửữự]', 'u', string)
    string = re.sub('[ÚÙỦŨỤƯỨỪỬỮỰ]', 'U', string)
    string = re.sub('[ýỳỷỹỵ]', 'y', string)
    string = re.sub('[ÝỲỶỸỴ]', 'Y', string)
    string = re.sub('đ', 'd', string)
    string = re.sub('Đ', 'D', string)
    string = string.lower()

    return string

def create_post(request):
    template_name = 'create_post.html'
    context = {}
    if request.method == 'POST':
        template_name = 'notification.html'
        title = request.POST['title']

        if Post.objects.filter(title=title).exists():
            context['notification'] = 'Tiêu đề bài viết đã được dùng'
        else:
            content = request.POST['content']
            status = request.POST['status']
            slug = slugify(remove_accent(title))
            print(content, slug, status)
            post = Post.objects.create(title=title, slug=slug, author=request.user, content=content, status=status)
            post.save()
            context['notification'] = 'Đăng bài thành công'

    return render(request, template_name, context)

def delete_post(request, slug):
    template_name = 'notification.html'
    post = get_object_or_404(Post, slug=slug)
    post.delete()
    context = {
        'notification': 'Đã xóa thành công'
    }
    return render(request, template_name, context)

def delete_comment(request, slug, pk):
    post = get_object_or_404(Post, slug=slug)
    comment = post.comments.filter(pk=pk)
    comment.delete()
    return redirect('post_detail', slug=post.slug)

def edit_comment(request, slug, pk):
    template_name = 'edit_comment.html'
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(pk=pk)
    context = {}
    if request.method == 'POST':
        comment_content = request.POST['content']
        post.comments.filter(pk=pk).update(body=comment_content)
        return redirect('post_detail', slug=slug)
    
    context['comments'] = comments
    context['post'] = post
    return render(request, template_name, context)

class SearchedList(generic.ListView):
    template_name = 'index.html'
    model = Post
    paginate_by = 5
    
    def get_queryset(self):
        query = self.request.GET.get('query')
        self.extra_context = {'query_result':query}
        if query:
            queryset = self.model.objects.filter(title__icontains=query)
        else:
            queryset = self.model.objects.none()
        return queryset