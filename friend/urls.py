from django.urls import path

from friend.views import SendFriendRequestView, FriendRequestView, AcceptFriendRequestView, RemoveFriendView, DeclineFriendView, CancelFriendRequestView, FriendsListView

app_name = 'friend'

urlpatterns = [
    path('friend_request/', SendFriendRequestView.as_view(), name='friend-request'),
    path('friend_requests/<user_id>/', FriendRequestView.as_view(), name='friend-requests'),
    path('friend_request_accept/<friend_request_id>/', AcceptFriendRequestView.as_view(), name='friend-request-accept'),
    path('friend_remove/', RemoveFriendView.as_view(), name='remove-friend'),
    path('friend_request_decline/<friend_request_id>/', DeclineFriendView.as_view(), name='friend-request-decline'),
    path('friend_request_cancel/', CancelFriendRequestView.as_view(), name='friend-request-cancel'),
    path('list/<user_id>', FriendsListView.as_view(), name='list'),

]
