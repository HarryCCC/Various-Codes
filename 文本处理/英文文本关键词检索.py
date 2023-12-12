def find_occurrences(text, target):
  # Initialize the start index to 0 and the occurrences list to an empty list
  start_index = 0
  occurrences = []
  # Split the text into a list of words
  words = text.split()
  # Iterate through the words
  for i, word in enumerate(words):
    # If the word is equal to the target string
    if word == target:
      # Add the index (i.e. the order of the word in the list) to the occurrences list
      occurrences.append(i + 1)
  # Return the list of occurrences
  return occurrences

# Test the function with some sample text and a target string
text = "This is a sample text is are am is are am is are am"
target = "is"
occurrences = find_occurrences(text, target)

# Print the number of occurrences and the list of indices
print(f"Number of occurrences: {len(occurrences)}")
print(f"Indices: {occurrences}")
