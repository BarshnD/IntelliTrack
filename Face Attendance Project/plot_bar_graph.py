import matplotlib.pyplot as plt
import numpy as np

# Read recognition scores from the file
with open("recognition_scores.txt", "r") as f:
    recognition_scores = [float(line.strip()) for line in f]

# Create a graph with the image number on the y-axis and recognition score on the x-axis
image_ids = np.arange(1, len(recognition_scores) + 1)  # Image numbers
plt.figure(figsize=(10, 6))
plt.barh(image_ids, recognition_scores, color='blue')  # Horizontal bar plot

# Labeling the graph
plt.title('Recognition Accuracy for Each Image')
plt.xlabel('Recognition Score (Lower is Better)')
plt.ylabel('Image Number')
plt.grid(True, axis='x')

# Save the graph as a vector graphic (SVG)
plt.savefig('recognition_accuracy_graph.svg', format='svg')

# Display the graph
plt.show()
