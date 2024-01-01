from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.views.generic import TemplateView, DetailView
from homepage.models import Project
from register.models import Account
from django.views.generic.edit import CreateView, UpdateView, DeleteView, BaseDeleteView, DeletionMixin
from homepage.forms import ProjectForm, ProfileUpdateForm
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.core.files.storage import default_storage, FileSystemStorage
import os
import cv2
import json
import base64
import requests
from django.conf import settings
from django.core import files

TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"


class HomeView(TemplateView):
    template_name = "home.html"


class ProjectsView(CreateView, ListView):
    form_class = ProjectForm
    model = Project
    success_url = reverse_lazy('homepage:projects')
    template_name = "projects.html"
    context_object_name = "projects"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.save()
        return super().form_valid(form)


class ProfileView(DetailView):
    template_name = "profile.html"
    model = Account
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'user'
    is_self = True
    is_friend = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and user.username != context["user"].username:
            self.is_self = False
        elif not user.is_authenticated:
            self.is_self = False
        context["is_self"] = self.is_self
        context["is_friend"] = self.is_friend
        return context


class ProfileSearch(ListView):
    template_name = "search_results.html"
    model = Account
    context_object_name = "accounts"

    def get_queryset(self):
        search_query = self.request.GET.get('q')
        accounts = []

        if search_query:
            search_results = Account.objects.filter(username__icontains=search_query)
            accounts = []
            print(search_results)
            for account in search_results:
                accounts.append((account, False))
        else:
            search_results = Account.objects.all()
            for account in search_results:
                accounts.append((account, False))
        return accounts


class EditProfileView(UpdateView):
    template_name = "edit_profile.html"
    model = Account
    form_class = ProfileUpdateForm
    #   fields = ['username', 'email', 'profile_image', 'hide_email']
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('homepage:profile')
    extra_context = {'DATA_UPLOAD_MAX_MEMORY_SIZE': settings.DATA_UPLOAD_MAX_MEMORY_SIZE}

    def form_valid(self, form):
        self.object = form.save()
        self.success_url = reverse_lazy('homepage:profile', kwargs={'username': self.request.user.username})
        return HttpResponseRedirect(self.get_success_url())


class DeleteProjectView(ListView, DeletionMixin):
    template_name = 'projects.html'
    model = Project
    success_url = reverse_lazy('homepage:projects')

    #   slug_field = 'name'
    #   slug_url_kwarg = 'delete'

    def post(self, request, *args, **kwargs):
        projects_to_delete = request.POST.getlist('project_ids')
        Project.objects.filter(id__in=projects_to_delete).delete()
        return HttpResponseRedirect(self.success_url)

    def get(self, request, *args, **kwargs):
        pass
        # projects_to_delete = request.
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                    self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    _("Empty list and “%(class_name)s.allow_empty” is False.")
                    % {
                        "class_name": self.__class__.__name__,
                    }
                )
        context = self.get_context_data()
        return self.render_to_response(context)


"""
    def form_valid(self, form):
        print("REQ= ", self.request.POST.get())
        print("FORM= ", form)
        print("REQ= ", json.loads(self.request))
        success_url = self.get_success_url()
        #self.object.delete()
        return HttpResponseRedirect(success_url)"""


def save_temp_profile_image_from_base64String(imageString, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)
        if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
            os.mkdir(settings.TEMP + "/" + str(user.pk))
        url = os.path.join(settings.TEMP + "/" + str(user.pk), TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(imageString)
        with storage.open('', 'wb+') as destination:
            destination.write(image)
            destination.close()
        return url
    except Exception as e:
        print("exception: " + str(e))
        # workaround for an issue I found
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            imageString += "=" * ((4 - len(imageString) % 4) % 4)
            return save_temp_profile_image_from_base64String(imageString, user)
    return None


def crop_image(request, *args, **kwargs):
    payload = {}
    user = request.user
    if request.POST and user.is_authenticated:
        try:
            imageString = request.POST.get("image")
            url = save_temp_profile_image_from_base64String(imageString, user)
            img = cv2.imread(url)

            cropX = int(float(str(request.POST.get("cropX"))))
            cropY = int(float(str(request.POST.get("cropY"))))
            cropWidth = int(float(str(request.POST.get("cropWidth"))))
            cropHeight = int(float(str(request.POST.get("cropHeight"))))
            if cropX < 0:
                cropX = 0
            if cropY < 0:
                cropY = 0
            crop_img = img[cropY:cropY + cropHeight, cropX:cropX + cropWidth]

            cv2.imwrite(url, crop_img)

            user.profile_image.delete()

            user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
            user.save()

            payload['result'] = "success"
            payload['cropped_profile_image'] = user.profile_image.url

            # delete temp file
            os.remove(url)

        except Exception as e:
            print("exception: " + str(e))
            payload['result'] = "error"
            payload['exception'] = str(e)
    return HttpResponse(json.dumps(payload), content_type="application/json")
