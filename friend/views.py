from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeletionMixin, BaseUpdateView, DeleteView
from django.views.generic.list import ListView
from friend.models import FriendRequest, FriendList
from register.models import Account
import json


class SendFriendRequestView(DetailView, UpdateView):
    template_name = "profile.html"
    model = FriendList
    # slug_field = 'username'
    # slug_url_kwarg = 'username'
    context_object_name = 'user'
    success_url = reverse_lazy('homepage:profile')

    def post(self, request, *args, **kwargs):
        # self.object = self.get_object()
        user = request.user
        payload = {}
        if user.is_authenticated:
            user_id = request.POST.get("receiver_user_id")
            if user_id:
                receiver = Account.objects.get(pk=user_id)
                try:
                    # Get any friend requests (active and not-active)
                    friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver)
                    # find if any of them are active (pending)
                    try:
                        for request in friend_requests:
                            if request.is_active:
                                raise Exception("Вы уже отправили запрос на дружбу этому пользователю.")
                        # If none are active create a new friend request
                        friend_request = FriendRequest(sender=user, receiver=receiver)
                        friend_request.save()
                        payload['response'] = "Запрос отправлен."
                    except Exception as e:
                        payload['response'] = str(e)
                except FriendRequest.DoesNotExist:
                    # There are no friend requests so create one.
                    friend_request = FriendRequest(sender=user, receiver=receiver)
                    friend_request.save()
                    payload['response'] = "Запрос отправлен."

                if payload['response'] == None:
                    payload['response'] = "Что-то пошло не так."
            else:
                payload['response'] = "Не удалось отправить запрос."
        else:
            payload['response'] = "Вы должны быть авторизованы, чтобы отправить запрос."
        return HttpResponse(json.dumps(payload), content_type="application/json")


class FriendRequestView(ListView):
    template_name = "friend/friend_requests.html"
    model = FriendRequest
    context_object_name = "friend_requests"

    def get_queryset(self):
        search_query = self.kwargs.get("user_id")
        print(self.kwargs.items())
        print(search_query)
        friend_requests = []
        user = self.request.user
        if user.is_authenticated:
            account = Account.objects.get(pk=search_query)
            if account == user:
                friend_requests = FriendRequest.objects.filter(receiver=account, is_active=True)
        return friend_requests


class AcceptFriendRequestView(BaseUpdateView):
    success_url = reverse_lazy('friend:friend-requests')
    model = FriendRequest

    def get(self, request, *args, **kwargs):
        user = request.user
        payload = {}
        if user.is_authenticated:
            friend_request_id = kwargs.get("friend_request_id")
            if friend_request_id:
                friend_request = FriendRequest.objects.get(pk=friend_request_id)
                print("HERE")
                print(friend_request.receiver)
                if friend_request.receiver == user:
                    if friend_request:
                        # found the request. Now accept it
                        updated_notification = friend_request.accept()
                        payload['response'] = "Friend request accepted."

                    else:
                        payload['response'] = "Something went wrong."
                else:
                    payload['response'] = "That is not your request to accept."
            else:
                payload['response'] = "Unable to accept that friend request."
        else:
            # should never happen
            payload['response'] = "You must be authenticated to accept a friend request."
        return HttpResponse(json.dumps(payload), content_type="application/json")


class RemoveFriendView(DeleteView):
    def post(self, request, *args, **kwargs):
        user = request.user
        payload = {}
        if request.method == "POST" and user.is_authenticated:
            user_id = request.POST.get("receiver_user_id")
            if user_id:
                try:
                    removee = Account.objects.get(pk=user_id)
                    friend_list = FriendList.objects.get(user=user)
                    friend_list.unfriend(removee)
                    payload['response'] = "Successfully removed that friend."
                except Exception as e:
                    payload['response'] = f"Something went wrong: {str(e)}"
            else:
                payload['response'] = "There was an error. Unable to remove that friend."
        else:
            # should never happen
            payload['response'] = "You must be authenticated to remove a friend."
        return HttpResponse(json.dumps(payload), content_type="application/json")


class DeclineFriendView(TemplateView):

    def get(self, request, *args, **kwargs):
        user = request.user
        payload = {}
        if request.method == "GET" and user.is_authenticated:
            friend_request_id = kwargs.get("friend_request_id")
            if friend_request_id:
                friend_request = FriendRequest.objects.get(pk=friend_request_id)
                # confirm that is the correct request
                if friend_request.receiver == user:
                    if friend_request:
                        # found the request. Now decline it
                        updated_notification = friend_request.decline()
                        payload['response'] = "Friend request declined."
                    else:
                        payload['response'] = "Something went wrong."
                else:
                    payload['response'] = "That is not your friend request to decline."
            else:
                payload['response'] = "Unable to decline that friend request."
        else:
            # should never happen
            payload['response'] = "You must be authenticated to decline a friend request."
        return HttpResponse(json.dumps(payload), content_type="application/json")


class CancelFriendRequestView(UpdateView):
    model = FriendRequest

    def post(self, request, *args, **kwargs):
        user = request.user
        payload = {}
        if request.method == "POST" and user.is_authenticated:
            user_id = request.POST.get("receiver_user_id")
            if user_id:
                receiver = Account.objects.get(pk=user_id)
                try:
                    friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver, is_active=True)
                except FriendRequest.DoesNotExist:
                    payload['response'] = "Nothing to cancel. Friend request does not exist."

                # There should only ever be ONE active friend request at any given time. Cancel them all just in case.
                if len(friend_requests) > 1:
                    for request in friend_requests:
                        request.cance()
                    payload['response'] = "Friend request canceled."
                else:
                    # found the request. Now cancel it
                    friend_requests.first().cancel()
                    payload['response'] = "Friend request canceled."
            else:
                payload['response'] = "Unable to cancel that friend request."
        else:
            # should never happen
            payload['response'] = "You must be authenticated to cancel a friend request."
        return HttpResponse(json.dumps(payload), content_type="application/json")


class FriendsListView(ListView):
    model = Account
    template_name = "friend/friend_list.html"

    def get(self, request, *args, **kwargs):
        context = {}
        user = request.user
        if user.is_authenticated:
            user_id = kwargs.get("user_id")
            if user_id:
                try:
                    this_user = Account.objects.get(pk=user_id)
                    context['this_user'] = this_user
                except Account.DoesNotExist:
                    return HttpResponse("That user does not exist.")
                try:
                    friend_list = FriendList.objects.get(user=this_user)
                except FriendList.DoesNotExist:
                    return HttpResponse(f"Could not find a friends list for {this_user.username}")

                # Must be friends to view a friends list
                if user != this_user:
                    if user not in friend_list.friends.all():
                        return HttpResponse("You must be friends to view their friends list.")
                friends = []  # [(friend1, True), (friend2, False), ...]
                # get the authenticated users friend list
                auth_user_friend_list = FriendList.objects.get(user=user)
                for friend in friend_list.friends.all():
                    friends.append((friend, auth_user_friend_list.is_mutual_friend(friend)))
                context['friends'] = friends
        else:
            return HttpResponse("You must be friends to view their friends list.")
        return render(request, "friend/friend_list.html", context)
