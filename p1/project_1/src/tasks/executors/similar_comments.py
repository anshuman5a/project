import numpy as np
from src.llm.client import LLMClient
from src.utils.file_ops import FileOps
import asyncio
from pathlib import Path

class SimilarCommentsExecutor:
    def __init__(self):
        self.llm_client = LLMClient()
        self.file_ops = FileOps()

    async def generate_embeddings(self, comments):
        # Use LLM to generate embeddings
        embeddings = []
        for comment in comments:
            prompt = f"Generate a numerical embedding vector for this text. Return a comma-separated list of 10 float values between -1 and 1: {comment}"
            try:
                embedding_str = await self.llm_client.generate(prompt)
                # Clean and convert embedding string to numpy array
                embedding = np.fromstring(
                    embedding_str.strip('[]').replace(' ', ''), 
                    sep=','
                )
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error generating embedding for comment: {comment}")
                embeddings.append(np.zeros(10))  # Fallback embedding
        return embeddings

    def cosine_similarity(self, vec1, vec2):
        # Ensure vectors are of same length and handle zero vectors
        if len(vec1) != len(vec2):
            vec1 = vec1[:min(len(vec1), len(vec2))]
            vec2 = vec2[:min(len(vec1), len(vec2))]
        
        # Avoid division by zero
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return np.dot(vec1, vec2) / (norm1 * norm2)

    async def find_most_similar_comments(self, comments):
        # Generate embeddings
        embeddings = await self.generate_embeddings(comments)
        
        # Find most similar pair
        max_similarity = -1
        most_similar_pair = None
        
        for i in range(len(comments)):
            for j in range(i+1, len(comments)):
                similarity = self.cosine_similarity(embeddings[i], embeddings[j])
                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar_pair = (comments[i], comments[j])
        
        return most_similar_pair

    async def execute(self, parameters):
        # Read comments from file


        project_root = Path(__file__).parent.parent.parent.parent 
        comments_path = project_root / "data/comments.txt"
        output_path = project_root / "data/comments-similar.txt"
        
        # comments_path = parameters.get('input_file', '/data/comments.txt')
        # output_path = parameters.get('output_file', '/data/comments-similar.txt')
        
        # Read comments
        comments_content = await self.file_ops.read_file(comments_path)
        comments = [comment.strip() for comment in comments_content.split('\n') if comment.strip()]
        
        # Find most similar comments
        similar_comments = await self.find_most_similar_comments(comments)
        
        # Write similar comments to output file
        output_content = '\n'.join(similar_comments) if similar_comments else "No similar comments found"
        await self.file_ops.write_file(output_path, output_content)
        
        return True