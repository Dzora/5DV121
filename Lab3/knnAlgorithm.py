# Author: dali@cs.umu.se
# Given as part of the course Fundamentals of Artificial Intelligence 2018.

# Import classifier, dataset and data formatting
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import *

# Import matlab stuff to produce plots
import matplotlib.pyplot as plt


def train_knn(x_train, y_train, k):
    """
    Given training data (input and output), train a k-NN classifier.

    Input:    x/y_train - Two arrays of equal length, one with input data and 
              one with the correct labels. 
              k - number of neighbors considered when training the classifier.
    Returns:  The trained classifier
    """
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(x_train, y_train)
    return knn

def evaluate_knn(knn, x_train, y_train, x_test, y_test):
    """
    Given a trained classifier, its training data, and test data, calculate
    the accuracy on the training and test sets.
    
    Input:    knn - A trained k-nn classifier
              x/y_train - Training data
              x/y_test  - Test data
    
    Returns:  A tuple (train_acc, test_acc) with the resulting accuracies,
              obtained when using the classifier on the given data.
    """
    train_score = knn.score(x_train, y_train)
    test_score = knn.score(x_test, y_test)
    return (train_score, test_score)

def load_dataset(name, features, test_size):
    """
    Loads the iris or breast cancer datasets with the given features and 
    train/test ratio.
    
    Input:    name - Either "iris" or "breastcancer"
              features - An array with the indicies of the features to load
              test_size - How large part of the dataset to be used as test data.
                          0.33 would give a test set 33% of the total size.
    Returns:  Arrays x_train, x_test, y_train, y_test that correspond to the
              training/test sets.
    """
    # Load the dataset
    if name == "iris":
        dataset = load_iris()
    elif name == "breastcancer":
        dataset = load_breast_cancer()
    
    print('You are using the features:')
    for x in features:
        print (x,"-", dataset.feature_names[x])
    
    X = dataset.data[:,features]
    Y = dataset.target
    
    # Split the dataset into a training and a test set
    #TODO choose a number as a seed (just to initialize the random number 
    # generator. 
    return train_test_split(X, Y, test_size=test_size, random_state=40)


if __name__ == '__main__':

    # Choose features to train on
    #TODO
    features = [0,1]
    #features = [0,1,2,3,4,5,6,7,8,9] 

    # The maximum value of k
    k_max = 30
    
    # Load the dataset with a test/training set ratio of 0.33
    #TODO choose dataset and set test size
    x_train, x_test, y_train, y_test = load_dataset("iris",features, 0.1)
    
    # Lists to save results in
    train_scores = []
    test_scores = []
    
    # Train the classifier with different values for k and save the accuracy 
    # achieved on the training and test sets
    #TODO
    for i in range(k_max):
        knn = train_knn(x_train,y_train,i+1)
        results = evaluate_knn(knn, x_train, y_train, x_test, y_test)
    
        train_scores.append(results[0])
        test_scores.append(results[1])
    
        print("Train-Scores: ", train_scores)
        print("Test-Scores: ", test_scores)
    
    # Construct plot
    plt.title('KNN results')
    plt.xlabel('Number of Neighbors K')
    plt.ylabel('Accuracy')
    
    # Create x-axis
    xaxis = [x for x in range(k_max)]
    
    # Plot the test and training scores with labels
    plt.plot(xaxis, train_scores, label='Training score')
    plt.plot(xaxis, test_scores, label='Test score')
    
    # Show the figure
    plt.legend()
    plt.show() 