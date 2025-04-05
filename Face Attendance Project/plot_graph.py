import matplotlib.pyplot as plt
import numpy as np

# Read recognition scores from the file
with open("recognition_scores.txt", "r") as f:
    recognition_scores = [float(line.strip()) for line in f]

# Create a linear graph with the image number on the x-axis and recognition score on the y-axis
image_ids = np.arange(1, len(recognition_scores) + 1)  # Image numbers

plt.figure(figsize=(10, 6))
plt.plot(image_ids, recognition_scores, marker='o', linestyle='-', color='blue', label='Recognition Score')

# Labeling the graph
plt.title('Recognition Accuracy for Each Image')
plt.xlabel('Image Number')
plt.ylabel('Recognition Score (Lower is Better)')
plt.grid(True)
plt.legend()

# Save the graph as a vector graphic (SVG)
plt.savefig('recognition_accuracy_graph.svg', format='svg')

# Display the graph
plt.show()
