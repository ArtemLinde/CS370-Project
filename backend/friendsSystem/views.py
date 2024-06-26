from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from requests import Response
from .serializers import FriendRequestSerializer, UserDetailSerializer
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Friend, FriendRequest
from userProjects.models import User, UserProfile
from .serializers import FriendSerializer
from django.db import models
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from rest_framework import generics, permissions
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from userProjects.serializers import UserProfileSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response



# Create your views here.

class FriendView(generics.RetrieveAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        other_username = self.kwargs.get('username')
        user = self.request.user
        other_user = get_object_or_404(User, username=other_username)

        # Check if users are friends
        is_Friend = Friend.objects.filter(
            (models.Q(friend1=user, friend2=other_user) | models.Q(friend1=other_user, friend2=user))
        ).exists()

        if is_Friend:
            return get_object_or_404(UserProfile, user=other_user)
        else:
            raise PermissionDenied('You are not friends with this user.')
    
class FriendListView(generics.ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        friends = Friend.objects.filter(models.Q(friend1=user) | models.Q(friend2=user))
        return friends

def getFriendsInfo(request):
    Currentuser = request.user.id
    friendslist = []
    # Filter friends by the current user
    friends = Friend.objects.filter(models.Q(friend1=Currentuser) | models.Q(friend2=Currentuser))
    for friend in friends:
        if friend.friend1 == request.user:
            friendslist.append(friend.friend2.username)
        else:
            friendslist.append(friend.friend1.username)
    return JsonResponse({'userfriends': friendslist})

@csrf_exempt 
def sendFriendRequest(request, sender_username, receiver_username):
    # Ensure both sender and receiver are valid users, including admins
    user1 = get_object_or_404(User, username=sender_username)
    user2 = get_object_or_404(User, username=receiver_username)

    # Prevent users from sending a friend request to themselves
    if user1 == user2:
        return JsonResponse({'error': 'You cannot send a match request to yourself'}, status=400)

    # Create or get the existing friend request
    friendReq, created = FriendRequest.objects.get_or_create(
        friendRequest_id = f"{user1.username}{user2.username}",
        reqSender=user1,
        reqReceiver=user2,
        defaults={'status': 'pending'}
    )

    if created:
        return HttpResponse('Friend request sent.')
    else:
        return HttpResponse('Friend request already sent.')
    
    """
    @csrf_exempt
def send_match_request(request, sender_username, receiver_username):
    user1 = get_object_or_404(User, username=sender_username)
    user2 = get_object_or_404(User, username=receiver_username)

    if user1 == user2:
        return JsonResponse({'error': 'You cannot send a match request to yourself'}, status=400)

    match, created = Match.objects.get_or_create(
        sender=user1,
        receiver=user2,
        defaults={'status': 'pending'}
    )

    if created:
        return JsonResponse({'message': 'Match request sent'})
    else:
        return JsonResponse({'message': 'Match request already exists'}, status=200)
    """

'''
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_friend_request(request, sender_username): 
    receiver = receiver = request.user 
    friend_request = get_object_or_404(FriendRequest, reqReceiver=receiver, reqSender=sender_username, status='pending')
    if (friend_request): 
        friend_request.status = 'accepted' 
        newFriend, created = Friend.objects.get_or_create(
                friend_id = f"{friend_request.reqSender.username}{friend_request.reqReceiver.username}",
                friend1 = get_object_or_404(User, username=friend_request.reqSender.username),
                friend2 = get_object_or_404(User, username=friend_request.reqReceiver.username),
                )
        return HttpResponse(('Friend request accepted.'))
    return HttpResponse('Request does not exist')
'''

@csrf_exempt
@permission_classes([IsAuthenticated])
def acceptFriendRequest(request, otherUser):
    user = request.user
    friend_reqs = FriendRequest.objects.filter(models.Q(reqReceiver=user))
    
    for req in friend_reqs:
            if (req.reqSender == get_object_or_404(User, username=otherUser)):
                newFriend, created = Friend.objects.get_or_create(
                friend_id = f"{req.reqSender.username}{req.reqReceiver.username}",
                friend1 = get_object_or_404(User, username=req.reqSender.username),
                friend2 = get_object_or_404(User, username=req.reqReceiver.username),
                )
                req.delete()
                return HttpResponse('Friend request accepted.')
    return HttpResponse('Request does not exist.')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_friend_request(request, sender_username):
    # The authenticated user is the receiver of the friend request
    
    receiver_username = request.user.username
    # Check if there is a pending friend request from sender to receiver
    
    try:
        friend_request = FriendRequest.objects.get(
            reqSender__username=sender_username,
            reqReceiver__username=receiver_username,
            status='pending'
        )
    except FriendRequest.DoesNotExist:
        return HttpResponse('Friend request not found.')

    # If the friend request exists and is pending, accept it
    if friend_request:
        friend_request.status = 'accepted'
        friend_request.save()

        # Create a new Friend object, unless it already exists
        friend_id = f"{sender_username}_{receiver_username}"
        new_friend, created = Friend.objects.get_or_create(
            friend_id=friend_id,
            defaults={
                'friend1': friend_request.reqSender,
                'friend2': friend_request.reqReceiver
            }
        )
        # If the Friend object was created, the friend request is accepted
        if created:
            return HttpResponse('Friend request accepted.')
        else:
            return HttpResponse('Friendship already exists.')

    return HttpResponse('Invalid request')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_friend_request(request, sender_username):
    # The authenticated user is the receiver of the friend request
    receiver_username = request.user.username

    # Check if there is a pending friend request from sender to receiver
    try:
        friend_request = FriendRequest.objects.get(
            reqSender__username=sender_username,
            reqReceiver__username=receiver_username,
            status='pending'
        )
    except FriendRequest.DoesNotExist:
        return HttpResponse('Friend request not found.')

    # If the friend request exists and is pending, reject it
    if friend_request:
        friend_request.status = 'rejected'
        friend_request.save()

        return HttpResponse('Friend request rejected.')

    return HttpResponse('Invalid request')


'''
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_match_request(request, sender_username): 
    receiver = request.user 
    match = get_object_or_404(Match, receiver=receiver, sender__username=sender_username, status='pending')
    match.status = 'accepted'
    match.save()
    return JsonResponse({'message': 'Match request accepted succesfully.'})
'''

'''
def rejectFriendRequest(request, otherUser):
    user = request.user
    friend_reqs = FriendRequest.objects.filter(models.Q(reqReceiver=user))
    
    for req in friend_reqs:
            if (req.reqSender == get_object_or_404(User, username=otherUser)):
                req.delete()
                return HttpResponse('Friend request rejected.')
    return HttpResponse('Request does not exist.')
'''

class OutgoingPendingRequestsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer
    def get_queryset(self):
        user = self.request.user
        request_relations = FriendRequest.objects.filter(
            models.Q(reqSender=user) | models.Q(reqReceiver=user)
        ).distinct()
        request_ids = set()

        for relation in request_relations:
            if relation.reqSender == user:
                request_ids.add(relation.reqReceiver.id)
        # Returns the users whom the current user has sent friend requests (not yet answered).
        return get_user_model().objects.filter(id__in=request_ids)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def view_friend_requests(request):
    current_user = request.user 
    friend_requests = FriendRequest.objects.filter(reqReceiver=current_user, status='pending')
    data = [
        {
            'sender': friend_request.reqSender.username, 
            'status': friend_request.status
        }
        for friend_request in friend_requests
    ]
    return JsonResponse(data, safe=False) 

'''
class IncomingPendingRequestsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer
    def get_queryset(self):
        user = self.request.user
        request_relations = FriendRequest.objects.filter(
            models.Q(reqSender=user) | models.Q(reqReceiver=user)
        ).distinct()
        request_ids = set()

        for relation in request_relations:
            if relation.reqReceiver == user:
                request_ids.add(relation.reqSender.id)
        # Returns the users whom the current user has not yet answered the requests for.
        return get_user_model().objects.filter(id__in=request_ids)
'''

@require_POST
@csrf_exempt
def removeFriend(request, self_username, friend_username):
    current_user = get_object_or_404(User, username=self_username)
    friend_user = get_object_or_404(User, username=friend_username)

    # Attempt to retrieve the friendship where the current user is either friend1 or friend2
    try:
        friend = Friend.objects.get(
            (Q(friend1=current_user) & Q(friend2__username=friend_username)) |
            (Q(friend2=current_user) & Q(friend1__username=friend_username))
        )
    except Friend.DoesNotExist:
        return JsonResponse({'error': 'Friendship not found.'}, status=404)

    # Check if the user is part of this friendship
    if friend.friend1 != current_user and friend.friend2 != current_user:
        raise PermissionDenied("You do not have permission to delete this friendship.")

    # Delete the friend relationship
    friend.delete()
    return JsonResponse({'message': 'Friendship deleted successfully.'})


class DetailedFriendListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_queryset(self):
        user = self.request.user
        friend_relations = Friend.objects.filter(
            models.Q(friend1=user) | models.Q(friend2=user)
        ).distinct()
        friend_ids = set()

        for relation in friend_relations:
            # Add both friend1 and friend2 ids, excluding the current user's id
            friend_ids.add(relation.friend1.id if relation.friend1 != user else relation.friend2.id)

        return get_user_model().objects.filter(id__in=friend_ids)
    
class FriendUserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        other_username = self.kwargs.get('username')
        other_user = get_object_or_404(User, username=other_username)

        return other_user.userprofile  # Assuming a related_name 'userprofile' on UserProfile model

class NonFriendsList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get current user
        current_user = request.user

        # Find all friends of the current user (both friend1 and friend2 relations)
        friends = Friend.objects.filter(
            models.Q(friend1=current_user) | models.Q(friend2=current_user)
        )

        # Extract user IDs of friends
        friend_ids = set()
        for friend in friends:
            if friend.friend1 == current_user:
                friend_ids.add(friend.friend2.id)
            else:
                friend_ids.add(friend.friend1.id)

        # Get all users who are not friends with the current user
        non_friends = User.objects.exclude(id__in=friend_ids)

        # Prepare a list of usernames
        usernames = [user.username for user in non_friends]

        return Response(data=usernames)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_pending_friend_requests(request, user_id):
    if request.user.id != int(user_id):
        return JsonResponse({'error': 'Unauthorized access'}, status=403)

    pending_requests = FriendRequest.objects.filter(reqReceiver_id=user_id, status='pending', notification_pending = True)
    if pending_requests.exists():
        
        serializer = FriendRequestSerializer(pending_requests, many=True)
        
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'message': 'None pending'}, status=204)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_as_sent_interaction(request, friend_request_id):
    try:
        friend_request = FriendRequest.objects.get(friendRequest_id=friend_request_id, reqSender=request.user, notification_interacted=False)
        friend_request.notification_interacted = True
        friend_request.save()
        return JsonResponse({'message': 'Notification marked as sent'}, status=200)
    except FriendRequest.DoesNotExist:
        return JsonResponse({'error': 'Friend request not found or already marked'}, status=404)
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_as_sent_pending(request, friend_request_id):
    try:
        friend_request = FriendRequest.objects.get(friendRequest_id=friend_request_id, reqReceiver=request.user, notification_pending=True)
        friend_request.notification_pending = False
        friend_request.save()
        return JsonResponse({'message': 'Notification marked as sent'}, status=200)
    except FriendRequest.DoesNotExist:
        return JsonResponse({'error': 'Friend request not found or already marked'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_friend_request_status(request, user_id):
    # Convert user_id from string to integer for comparison (if needed)
    user_id = int(user_id)
    # Ensure the request.user.id matches the provided user_id to avoid unauthorized access
    if request.user.id != user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Fetch only the friend requests where notification has not been sent yet
    friend_requests = FriendRequest.objects.filter(reqSender_id=user_id, notification_interacted=False).exclude(status='pending')

    if friend_requests.exists():
        # Serialize the data
        serializer = FriendRequestSerializer(friend_requests, many=True)
        
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'message': 'No updates'}, status=204)
