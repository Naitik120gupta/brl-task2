from rest_framework import viewsets
from .serializers import NoteSerializer
from .models import Notes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
import json
from django.template.loader import render_to_string
from django.contrib.auth import login 
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect
from social_django.utils import load_strategy, load_backend



@api_view(['POST'])
def register_user(request):
    data = request.data
    if User.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'])
    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

# Password reset views
#  def destroy_queryset(self, request, *args, **kwargs):
#     try:
#             Notes.objects.filter(user=request.user).delete()  
#             return Response({
#                 'status': True,
#                 'message': 'All Notes deleted successfully.'
#             })
#     except Exception as e:
#             return Response({
#                 "msg":e
#             })

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def notes_list(request):
    if request.method == 'GET':
        notes = Notes.objects.filter(user=request.user)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate the note with the authenticated user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        Notes.objects.filter(user=request.user).delete()
        return Response({'message': 'All notes deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def note_detail(request):
    note_id = request.query_params.get('NoteID')
    try:
        note = Notes.objects.get(id=note_id, user=request.user)
    except Notes.DoesNotExist:
        return Response({'error': 'Note not found or not authorized'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = NoteSerializer(note)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = NoteSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = NoteSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    elif request.method == 'DELETE':
        note.delete()
        return Response({'message': 'Note deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    # To reset password without token
@api_view(['POST'])
@permission_classes([AllowAny])
def ResetPassword(request):
    email = request.data.get('email')

    if not email:
        return JsonResponse({"error": "Email is required."}, status=400)

    try:
        user = User.objects.get(email=email)
        password_reset_link = "http://localhost:8000/pass/reset/"
        subject = "Password Reset Requested"
        message = render_to_string('reset.html', {
            'password_reset_link': password_reset_link,
            'username': user.username,
        })

        send_mail(subject, message, 'naitik12gupta05@gmail.com', [email])
        return JsonResponse({"message": "Password reset link sent."}, status=200)
    
    # except ObjectDoesNotExist:
    #     return JsonResponse({"error": "User with this email does not exist."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    


# Reset Password with token
def passwordResetToken(request,token):
    email = request.data.get('email')

    if not email:
        return JsonResponse({"error": "Email is required."}, status=400)

    try:
        user = User.objects.get(email=email)
        password_reset_link = f"http://localhost:8000/pass/reset/{token}"

        subject = "Password Reset Requested"
        message = render_to_string('reset.html', {
            'password_reset_link': password_reset_link,
            'username': user.username,
        })

        send_mail(subject, message, 'naitik12gupta05@gmail.com', [email])
        return JsonResponse({"message": "Password reset link sent."}, status=200)
    
    # except ObjectDoesNotExist:
    #     return JsonResponse({"error": "User with this email does not exist."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    


# #  to change password from link through email
@api_view(['POST'])
def UserPassReset(request):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    username = request.data.get('username')
    new_password = request.data.get('password')

    try:
        user = User.objects.get(username=username) 
        user.set_password(new_password) 
        user.save()  
        return Response({'message': 'Password updated successfully'})
    except Exception as e:
        return Response({
            'error': e
        })

def google_login(request):
    strategy = load_strategy(request)
    backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=None)
    return redirect(backend.auth_url())

def google_callback(request):
    # Get the logged-in user's social account info from Django Allauth
    user = request.user

    strategy = load_strategy(request)
    backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=None)
    
    # Complete the authentication
    user = backend.do_auth(request.GET.get('code'))
    
    if user and user.is_active:
        login(request, user)  # Log the user in

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    else:
        return Response({"error": "Authentication failed"}, status=400)
    
@api_view(['GET'])
def FetchAllNotes(request):
    try:
        notes = Notes.objects.all()
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            "msg":e
        })