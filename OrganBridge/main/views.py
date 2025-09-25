# backend/donation/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from . import models, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from userauth import models as userauth_models
from ml_services import organ_matching_service

class OrganDonorView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create or update organ donation information"""
        try:
            donor = userauth_models.Donor.objects.filter(user=request.user).first()
            if not donor:
                return Response({'message': 'Donor profile not found'}, status=404)
            organ, created = models.Organ.objects.get_or_create(
                donor=donor,
                defaults={
                    'blood_group': request.data.get('blood_group'),
                    'organ': request.data.get('organ'),
                    'organ_date_time': request.data.get('organ_date_time'),
                    'smoke': request.data.get('smoke', False),
                    'alcohol': request.data.get('alcohol', False),
                    'drug': request.data.get('drug', False),
                    'avg_sleep': request.data.get('avg_sleep', 8),
                    'daily_exercise': request.data.get('daily_exercise', 0),
                }
            )
            if not created:
                for field, value in request.data.items():
                    if hasattr(organ, field):
                        setattr(organ, field, value)
                organ.save()
            serializer = serializers.OrganSerializer(organ)
            return Response({'message': 'Organ information saved successfully', 'data': serializer.data})
        except Exception as e:
            return Response({'message': f'Error: {str(e)}'}, status=500)
    
    def get(self, request):
        """Get donor's organ information"""
        try:
            donor = userauth_models.Donor.objects.filter(user=request.user).first()
            if not donor:
                return Response({'message': 'Donor profile not found'}, status=404)
            organ = models.Organ.objects.filter(donor=donor).first()
            if not organ:
                return Response({'message': 'No organ information found'}, status=404)
            serializer = serializers.OrganSerializer(organ)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': f'Error: {str(e)}'}, status=500)

class FindOrganMatchesView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Find organ matches for a recipient"""
        try:
            recipient = userauth_models.Recipient.objects.filter(user=request.user).first()
            if not recipient:
                return Response({'message': 'Recipient profile not found'}, status=404)
            recipient_profile = {
                'city': recipient.city,
                'blood_group': recipient.blood_group,
                'organ': recipient.organ,
                'age': request.data.get('age', ''),
                'gender': request.data.get('gender', ''),
                'race': request.data.get('race', ''),
            }
            matches = organ_matching_service.find_matches(
                recipient_profile, 
                n_matches=request.data.get('n_matches', 10)
            )
            return Response({'matches': matches, 'total_found': len(matches)})
        except Exception as e:
            return Response({'message': f'Error: {str(e)}'}, status=500)

class CompatibilityCheckView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Check compatibility between donor and recipient"""
        try:
            donor_id = request.data.get('donor_id')
            recipient_id = request.data.get('recipient_id')
            if not donor_id or not recipient_id:
                return Response({'message': 'Both donor_id and recipient_id are required'}, status=400)
            donor = userauth_models.Donor.objects.filter(id=donor_id).first()
            recipient = userauth_models.Recipient.objects.filter(id=recipient_id).first()
            if not donor or not recipient:
                return Response({'message': 'Donor or recipient not found'}, status=404)
            donor_profile = {
                'city': donor.city,
                'blood_group': request.data.get('donor_blood_group', ''),
                'organ': request.data.get('organ', ''),
            }
            recipient_profile = {
                'city': recipient.city,
                'blood_group': recipient.blood_group,
                'organ': recipient.organ,
            }
            compatibility_score = organ_matching_service.get_compatibility_score(
                donor_profile, recipient_profile
            )
            return Response({
                'compatibility_score': compatibility_score,
                'donor_info': {'name': donor.user.username, 'city': donor.city},
                'recipient_info': {'name': recipient.user.username, 'city': recipient.city, 'organ_needed': recipient.organ}
            })
        except Exception as e:
            return Response({'message': f'Error: {str(e)}'}, status=500)

class AvailableDonorsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of available donors with their organ information"""
        try:
            organs = models.Organ.objects.select_related('donor__user').all()
            donors_data = []
            for organ in organs:
                donor_info = {
                    'id': organ.donor.id,
                    'name': organ.donor.user.username,
                    'city': organ.donor.city,
                    'blood_group': organ.blood_group,
                    'organ': organ.organ,
                    'organ_date': organ.organ_date_time,
                    'health_info': {
                        'smoke': organ.smoke,
                        'alcohol': organ.alcohol,
                        'drug': organ.drug,
                        'avg_sleep': organ.avg_sleep,
                        'daily_exercise': organ.daily_exercise,
                    }
                }
                donors_data.append(donor_info)
            return Response({'donors': donors_data, 'total_count': len(donors_data)})
        except Exception as e:
            return Response({'message': f'Error: {str(e)}'}, status=500)

class PostAuthor(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = [IsAuthenticated]

    def get(self, request):
        author = userauth_models.Recipient.objects.filter(user=request.user).first()
        posts = models.Post.objects.filter(author=author)
        serializer = serializers.PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        author = userauth_models.Recipient.objects.filter(user=request.user).first()
        if author:
            post = models.Post.objects.filter(author=author).first()
            if not post:
                models.Post.objects.create(author=author, **request.data)
                return Response({'message': 'Successfully created post'})
            return Response({'message': 'You already have a post'})
        return Response({'message': 'Failed to create post'})

    def delete(self, request):
        author = userauth_models.Recipient.objects.filter(user=request.user).first()
        if author:
            posts = models.Post.objects.filter(author=author).first()
            if posts:
                posts.delete()
                return Response({'message': 'Successfully deleted post'})
            return Response({'message': 'You do not have a post'})
        return Response({'message': 'Invalid request'})
        
    def put(self, request):
        author = userauth_models.Recipient.objects.filter(user=request.user).first()
        if author:
            posts = models.Post.objects.filter(author=author).first()
            if posts:
                for attr, value in request.data.items():
                    setattr(posts, attr, value)
                posts.save()
                return Response({'message': 'Successfully changed post'})
            return Response({'message': 'You do not have a post'})
        return Response({'message': 'Invalid request'})

class PostEveryone(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = models.Post.objects.all()
        serializer = serializers.PostSerializer(posts, many=True)
        return Response(serializer.data)

class DonorSignUp(APIView):
    permission_classes = []
    def post(self, request):
        serializer = serializers.DonorUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Successfully created ID'})
        else:
            return Response(serializer.errors)

class RecipientSignUp(APIView):
    permission_classes = []
    def post(self, request):
        serializer = serializers.RecipientUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Successfully created ID'})
        else:
            return Response(serializer.errors)

class GETRecipient(APIView):
    permission_classes = []
    def get(self, request):
        req = userauth_models.Recipient.objects.all()
        serializer = serializers.RecipientSerializer(req, many=True)
        return Response(serializer.data)