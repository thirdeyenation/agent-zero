import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns

# Simulate user preferences and content data
np.random.seed(42)
users = np.random.randint(1, 100, 1000)
content = np.random.randint(1, 50, 1000)
ratings = np.random.randint(1, 6, 1000)

# Create a DataFrame
data = pd.DataFrame({'user_id': users, 'content_id': content, 'rating': ratings})

# Pivot the data to create a user-content matrix
user_content_matrix = data.pivot_table(index='user_id', columns='content_id', values='rating').fillna(0)

# Calculate cosine similarity between users
user_similarity = cosine_similarity(user_content_matrix)
user_similarity_df = pd.DataFrame(user_similarity, index=user_content_matrix.index, columns=user_content_matrix.index)

# Function to get similar users
def get_similar_users(user_id, user_similarity_df, n=5):
    similar_users = user_similarity_df[user_id].sort_values(ascending=False).index[1:n+1]
    return similar_users

# Example: Get similar users for user 1
similar_users = get_similar_users(1, user_similarity_df)
print('Similar users to user 1:', similar_users)

# Visualize user similarity
plt.figure(figsize=(10, 8))
sns.heatmap(user_similarity_df, cmap='YlGnBu')
plt.title('User Similarity Matrix')
plt.show()

# Reinforcement Learning Model
class RecommendationModel(tf.keras.Model):
    def __init__(self, num_users, num_content, embedding_size):
        super(RecommendationModel, self).__init__()
        self.user_embedding = tf.keras.layers.Embedding(num_users, embedding_size)
        self.content_embedding = tf.keras.layers.Embedding(num_content, embedding_size)
        self.dense = tf.keras.layers.Dense(1, activation='sigmoid')

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

# Train the model
history = model.fit(X_train, y_train, epochs=10, batch_size=64, validation_data=(X_test, y_test))

# Plot training history
plt.figure(figsize=(10, 6))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Training History')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()