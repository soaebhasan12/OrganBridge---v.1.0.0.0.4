# i am successfully created and activated venv in backend folder of the project. but when i am pressing ctrl+shift+p, i can not see the path of our activated environment, which consist our all dependencies.# backend/train_model.py




"""
Machine Learning Model Training Script
Extracted from Jupyter notebook for organ matching system
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity

def create_ml_models_directory():
    """Create directory for ML models if it doesn't exist"""
    if not os.path.exists('ml_models'):
        os.makedirs('ml_models')
        print("Created ml_models directory")

def load_and_preprocess_data():
    """Load and preprocess the kidney data"""
    print("Loading and preprocessing data...")
    
    # Load the data - make sure KidneyData.csv is in the same directory
    try:
        data = pd.read_csv('D:\\PYTHON-PRACTICE\\03-DJANGO PROJECTS PRACTICE\\OrganBridge\\OrganBrodge\\backend\\ml_models\\KidneyData.csv')  # Adjust path if needed
        print(f"Data loaded successfully. Shape: {data.shape}")
    except FileNotFoundError:
        print("Error: KidneyData.csv not found. Please ensure it's in the current directory.")
        return None
    
    # Drop Time column if exists
    if 'Time' in data.columns:
        data = data.drop(columns=['Time'])
        print("Dropped 'Time' column")
    
    # Convert all columns to string (except Delta if you want to keep it)
    columns_to_convert = ['Gender', 'Race', 'Age', 'Blood Type', 'PosNeg', 
                         'Smoke', 'Drug', 'Alcohol', 'AvgSleep', 'City']
    
    for col in columns_to_convert:
        if col in data.columns:
            data[col] = data[col].astype(str)
    
    # Create category column by combining features
    category_cols = ['Gender', 'Race', 'Age', 'Blood Type', 'PosNeg', 
                    'Smoke', 'Drug', 'Alcohol', 'AvgSleep']
    
    # Filter only existing columns
    existing_cols = [col for col in category_cols if col in data.columns]
    
    data['category'] = data['City'].str.cat(data[existing_cols], sep=',')
    print("Created 'category' column")
    
    return data

def train_tfidf_model(data):
    """Train TF-IDF model"""
    print("Training TF-IDF model...")
    
    # Create TF-IDF vectorizer
    tf_model = TfidfVectorizer(
        max_features=200,
        max_df=0.25,
        min_df=0.01,
        stop_words='english'
    )
    
    # Create corpus from categories
    corpus = data['category']
    
    # Fit and transform the corpus
    tf_matrix = tf_model.fit_transform(corpus)
    
    print(f"TF-IDF matrix shape: {tf_matrix.shape}")
    
    return tf_model, tf_matrix

def train_nearest_neighbors(tf_matrix):
    """Train Nearest Neighbors model"""
    print("Training Nearest Neighbors model...")
    
    nn_model = NearestNeighbors(n_neighbors=50, algorithm='ball_tree')
    nn_model.fit(tf_matrix)
    
    print("Nearest Neighbors model trained successfully")
    return nn_model

def calculate_cosine_similarity(tf_matrix):
    """Calculate cosine similarity matrix"""
    print("Calculating cosine similarity matrix...")
    
    cosine_sim = cosine_similarity(tf_matrix, tf_matrix)
    print(f"Cosine similarity matrix shape: {cosine_sim.shape}")
    
    return cosine_sim

def save_models(tf_model, tf_matrix, cosine_sim, nn_model):
    """Save all models to files"""
    print("Saving models...")
    
    # Save TF-IDF model
    with open('ml_models/tf_model.pkl', 'wb') as f:
        pickle.dump(tf_model, f)
    print("Saved tf_model.pkl")
    
    # Save TF-IDF matrix
    with open('ml_models/tf_matrix.pkl', 'wb') as f:
        pickle.dump(tf_matrix, f)
    print("Saved tf_matrix.pkl")
    
    # Save cosine similarity matrix
    np.save('ml_models/cosine_sim.npy', cosine_sim)
    print("Saved cosine_sim.npy")
    
    # Save Nearest Neighbors model
    with open('ml_models/nn_model.pkl', 'wb') as f:
        pickle.dump(nn_model, f)
    print("Saved nn_model.pkl")

def test_model(tf_model, nn_model, data):
    """Test the trained model with a sample query"""
    print("\nTesting the model...")
    
    # Test case
    ideal_category = ['AB, Neg, Seattle']
    
    try:
        # Transform the test case
        new = tf_model.transform(ideal_category)
        
        # Find neighbors
        results = nn_model.kneighbors(new.todense())
        
        print(f"Test successful! Found {len(results[1][0])} matches")
        print(f"First match: {data['category'].iloc[results[1][0][0]]}")
        
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def main():
    """Main function to train and save all models"""
    print("Starting ML model training...")
    
    # Create models directory
    create_ml_models_directory()
    
    # Load and preprocess data
    data = load_and_preprocess_data()
    if data is None:
        return
    
    # Train TF-IDF model
    tf_model, tf_matrix = train_tfidf_model(data)
    
    # Train Nearest Neighbors
    nn_model = train_nearest_neighbors(tf_matrix)
    
    # Calculate cosine similarity
    cosine_sim = calculate_cosine_similarity(tf_matrix)
    
    # Save all models
    save_models(tf_model, tf_matrix, cosine_sim, nn_model)
    
    # Test the model
    test_successful = test_model(tf_model, nn_model, data)
    
    if test_successful:
        print("\n✅ Model training completed successfully!")
        print("Models saved in 'ml_models' directory")
        print("You can now copy these files to your Django backend")
    else:
        print("\n❌ Model training completed but testing failed")
    
    # Copy data file to ml_models directory
    try:
        data.to_csv('ml_models/processed_data.csv', index=False)
        print("Saved processed data to ml_models/processed_data.csv")
    except Exception as e:
        print(f"Error saving processed data: {e}")

if __name__ == "__main__":
    main()