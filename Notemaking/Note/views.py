from rest_framework import status
from rest_framework.response import Response
from .models import Notes
from .serializers import NoteSerializer
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django_rest_passwordreset.views import ResetPasswordRequestToken, ResetPasswordConfirm


@api_view(['POST'])
def register_user(request):
    data = request.data
    if User.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'])
    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

# Password reset views
class PasswordResetView(ResetPasswordRequestToken):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class PasswordResetConfirmView(ResetPasswordConfirm):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def notes_list(request):
    # GET: Retrieve all notes for the authenticated user
    if request.method == 'GET':
        notes = Notes.objects.filter(user=request.user)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)
    
    # POST: Create a new note for the authenticated user
    elif request.method == 'POST':
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate the note with the authenticated user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE: Delete all notes for the authenticated user
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
    
    # GET: Fetch a particular note
    if request.method == 'GET':
        serializer = NoteSerializer(note)
        return Response(serializer.data)
    
    # PUT: Replace the note
    elif request.method == 'PUT':
        serializer = NoteSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH: Update specific fields of the note
    elif request.method == 'PATCH':
        serializer = NoteSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE: Delete the note
    elif request.method == 'DELETE':
        note.delete()
        return Response({'message': 'Note deleted successfully'}, status=status.HTTP_204_NO_CONTENT)