import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity, pearsonr
from sklearn.metrics import precision_score, recall_score, ndcg_score
import tensorflow as tf
from tensorflow.keras.layers import Embedding, Dense, Flatten
from tensorflow.keras.models import Model
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Simulate more realistic user preferences and content data
np.random.seed(42)
num_users = 1000
num_content = 50
users = np.random.randint(1, num_users + 1, 5000)
content = np.random.randint(1, num_content + 1, 5000)
ratings = np.random.randint(1, 6, 5000)

# Add metadata to content
content_metadata = pd.DataFrame({
    'content_id': np.arange(1, num_content + 1),
    'genre': np.random.choice(['Action', 'Comedy', 'Drama', 'Sci-Fi', 'Documentary'], num_content),
    'category': np.random.choice(['Movie', 'TV Show', 'Podcast', 'Educational'], num_content)
})

# Create a DataFrame
data = pd.DataFrame({'user_id': users, 'content_id': content, 'rating': ratings})

# Pivot the data to create a user-content matrix
user_content_matrix = data.pivot_table(index='user_id', columns='content_id', values='rating').fillna(0)

# Calculate cosine similarity and Pearson correlation between users
user_similarity_cosine = cosine_similarity(user_content_matrix)
user_similarity_pearson = np.array([[pearsonr(user_content_matrix.iloc[i], user_content_matrix.iloc[j])[0] for j in range(len(user_content_matrix))] for i in range(len(user_content_matrix))])

# Function to get similar users using different metrics
def get_similar_users(user_id, user_similarity_df, n=5):
    similar_users_cosine = user_similarity_cosine[user_id].argsort()[-n-1:-1][::-1]
    similar_users_pearson = user_similarity_pearson[user_id].argsort()[-n-1:-1][::-1]
    return similar_users_cosine, similar_users_pearson

# Example: Get similar users for user 1
similar_users_cosine, similar_users_pearson = get_similar_users(1, user_similarity_cosine)
print('Similar users to user 1 (Cosine):', similar_users_cosine)
print('Similar users to user 1 (Pearson):', similar_users_pearson)

# Visualize user similarity
plt.figure(figsize=(10, 8))
sns.heatmap(user_similarity_cosine, cmap='YlGnBu')
plt.title('User Similarity Matrix (Cosine)')
plt.show()

plt.figure(figsize=(10, 8))
sns.heatmap(user_similarity_pearson, cmap='YlGnBu')
plt.title('User Similarity Matrix (Pearson)')
plt.show()

# Reinforcement Learning Model
class RecommendationModel(Model):
    def __init__(self, num_users, num_content, embedding_size):
        super(RecommendationModel, self).__init__()
        self.user_embedding = Embedding(num_users, embedding_size)
        self.content_embedding = Embedding(num_content, embedding_size)
        self.dense = Dense(1, activation='sigmoid')

    def call(self, inputs):
        user_vector = self.user_embedding(inputs[:, 0])
        content_vector = self.content_embedding(inputs[:, 1])
        dot_product = tf.reduce_sum(user_vector * content_vector, axis=1)
        return self.dense(tf.expand_dims(dot_product, axis=1))

# Prepare data for the model
user_ids = data['user_id'].values
content_ids = data['content_id'].values
ratings = data['rating'].values

# Split the data
X = np.array(list(zip(user_ids, content_ids)))
y = ratings
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and compile the model
model = RecommendationModel(num_users=max(user_ids)+1, num_content=max(content_ids)+1, embedding_size=50)
model.compile(optimizer='adam', loss='mse')

# Train the model with early stopping
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)
history = model.fit(X_train, y_train, epochs=20, batch_size=64, validation_data=(X_test, y_test), callbacks=[early_stopping])

# Plot training history
plt.figure(figsize=(10, 6))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Training History')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

# Evaluate the model
y_pred = model.predict(X_test)
precision = precision_score(y_test, np.round(y_pred), average='micro')
recall = recall_score(y_test, np.round(y_pred), average='micro')
ndcg = ndcg_score([y_test], [y_pred.flatten()])
print(f'Precision: {precision}, Recall: {recall}, NDCG: {ndcg}')

# Visualize user-content embeddings
user_embeddings = model.user_embedding.weights[0].numpy()
content_embeddings = model.content_embedding.weights[0].numpy()

fig = px.scatter_3d(x=user_embeddings[:, 0], y=user_embeddings[:, 1], z=user_embeddings[:, 2], title='User Embeddings')
fig.show()

fig = px.scatter_3d(x=content_embeddings[:, 0], y=content_embeddings[:, 1], z=content_embeddings[:, 2], title='Content Embeddings')
fig.show()