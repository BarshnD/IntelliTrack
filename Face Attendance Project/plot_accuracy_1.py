import matplotlib.pyplot as plt
import numpy as np

# Example data: Replace this with your actual recognition data
# For this example, we assume the recognition accuracy score is between 0 and 100
# where 0 is a perfect match and higher values represent less accurate recognition
image_ids = np.arange(1, 101)  # Image numbers from 1 to 100
recognition_scores = np.random.uniform(20, 80, 100)  # Random recognition scores for illustration

# Plotting the accuracy graph
plt.figure(figsize=(10, 6))
plt.barh(image_ids, recognition_scores, color='blue')  # Horizontal bar plot

# Labeling the graph
plt.title('Recognition Accuracy for 100 Images')
plt.xlabel('Recognition Score (Lower is Better)')
plt.ylabel('Image Number')
plt.grid(True, axis='x')

# Save the graph as a vector graphic (SVG)
plt.savefig('recognition_accuracy_graph.svg', format='svg')

# Display the graph
plt.show()
