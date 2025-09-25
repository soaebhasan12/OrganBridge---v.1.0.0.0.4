# backend/ml_service.py
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
import os
from django.conf import settings

class OrganMatchingService:
    def __init__(self):
        self.tf_model = None
        self.tf_matrix = None
        self.nn_model = None
        self.data = None
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models and data"""
        try:
            # Define paths for model files
            model_dir = os.path.join(settings.BASE_DIR, 'ml_models')
            
            # Load TF-IDF model
            with open(os.path.join(model_dir, 'tf_model.pkl'), 'rb') as f:
                self.tf_model = pickle.load(f)
            
            # Load TF-IDF matrix
            with open(os.path.join(model_dir, 'tf_matrix.pkl'), 'rb') as f:
                self.tf_matrix = pickle.load(f)
            
            # Load training data
            self.data = pd.read_csv(os.path.join(model_dir, 'KidneyData.csv'))
            self.prepare_data()
            
            # Initialize and fit NearestNeighbors
            self.nn_model = NearestNeighbors(n_neighbors=10, algorithm='ball_tree')
            self.nn_model.fit(self.tf_matrix)
            
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def prepare_data(self):
        """Prepare data similar to the notebook"""
        # Drop Time column if exists
        if 'Time' in self.data.columns:
            self.data = self.data.drop(columns=['Time'])
        
        # Convert all columns to string
        for col in self.data.columns:
            if col != 'Delta':
                self.data[col] = self.data[col].astype(str)
        
        # Create category column
        category_cols = ['Gender', 'Race', 'Age', 'Blood Type', 'PosNeg', 
                        'Smoke', 'Drug', 'Alcohol', 'AvgSleep']
        self.data['category'] = self.data['City'].str.cat(
            self.data[category_cols], sep=','
        )
    
    def find_matches(self, recipient_profile, n_matches=5):
        """
        Find organ matches for a recipient
        
        Args:
            recipient_profile (dict): Recipient's profile information
            n_matches (int): Number of matches to return
        
        Returns:
            list: List of matched donor profiles
        """
        try:
            # Create search query from recipient profile
            query_parts = []
            
            # Add relevant fields to query
            if 'city' in recipient_profile:
                query_parts.append(recipient_profile['city'])
            if 'blood_group' in recipient_profile:
                query_parts.append(recipient_profile['blood_group'])
            if 'organ' in recipient_profile:
                query_parts.append(recipient_profile['organ'])
            
            query_string = ', '.join(query_parts)
            
            if not query_string:
                return []
            
            # Transform query using TF-IDF
            query_vector = self.tf_model.transform([query_string])
            
            # Find nearest neighbors
            distances, indices = self.nn_model.kneighbors(
                query_vector.todense(), n_neighbors=n_matches
            )
            
            # Get matched profiles
            matches = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.data):
                    match_data = self.data.iloc[idx]
                    matches.append({
                        'index': int(idx),
                        'distance': float(distances[0][i]),
                        'category': match_data['category'],
                        'delta': match_data['Delta'],
                        'similarity_score': 1 - (distances[0][i] / 2)  # Convert distance to similarity
                    })
            
            return matches
            
        except Exception as e:
            print(f"Error finding matches: {e}")
            return []
    
    def get_compatibility_score(self, donor_profile, recipient_profile):
        """
        Calculate compatibility score between donor and recipient
        
        Args:
            donor_profile (dict): Donor's profile
            recipient_profile (dict): Recipient's profile
        
        Returns:
            float: Compatibility score (0-1)
        """
        try:
            # Create profiles for comparison
            donor_query = self.create_profile_string(donor_profile)
            recipient_query = self.create_profile_string(recipient_profile)
            
            # Transform both profiles
            donor_vector = self.tf_model.transform([donor_query])
            recipient_vector = self.tf_model.transform([recipient_query])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(donor_vector, recipient_vector)[0][0]
            
            return float(similarity)
            
        except Exception as e:
            print(f"Error calculating compatibility: {e}")
            return 0.0
    
    def create_profile_string(self, profile):
        """Create a string representation of a profile for TF-IDF"""
        parts = []
        
        # Add relevant fields
        fields = ['city', 'gender', 'race', 'age', 'blood_group', 
                 'organ', 'smoke', 'drug', 'alcohol', 'avg_sleep']
        
        for field in fields:
            if field in profile and profile[field]:
                parts.append(str(profile[field]))
        
        return ', '.join(parts)

# Initialize the service
organ_matching_service = OrganMatchingService()