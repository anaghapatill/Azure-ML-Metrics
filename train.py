# IMPORT LIBRARIES
from sklearn.datasets import load_svmlight_file
from sklearn.metrics import f1_score, accuracy_score, average_precision_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
# IMPORT AZURE LIBRARY
from azureml.core.run import Run


# DEFINE FUNCTIONS
def get_data(filepath):
    data = load_svmlight_file(filepath)
    return data[0], data[1]


def Classifier_Test_Train(model, model_name):
    # Training Model
    model.fit(X_train, y_train)

    # Testing Model
    predictions = model.predict(X_test)
    accuracy = round(accuracy_score(y_test, predictions),2)
    f1score = round(f1_score(y_test, predictions), 2)
    precision = round(average_precision_score(y_test, predictions),2)

    # AZURE LOGGING VARIABLES
    run_logger = Run.get_context()
    run_logger.log(name='Model', value=model_name)
    run_logger.log(name='Accuracy', value=accuracy)
    run_logger.log(name='F1 Score', value=f1score)
    run_logger.log(name='Precision', value=precision)
    


# MAIN FUNCTION
if __name__ == '__main__':
    run = Run.get_context()

    # IMPORT DATA
    X_train, y_train = get_data("./data/train_data.txt")
    X_test, y_test = get_data("./data/test_data.txt")

    X_train = X_train.toarray()  # convert sparce matrix to array
    X_test = X_test.toarray()

    # UNCOMMENT BELOW CODE BASED ON REQUIRED MODEL
    
    
    # RFC
    model_type = RandomForestClassifier()
    model_name = "Random Forest"
    
    
    '''
    # NN

    model_type = MLPClassifier()
    model_name = "Neural Networks"
    '''
    
    '''
    #KNN
    
    model_type = KNeighborsClassifier()
    model_name = "K Nearest Neighbor"
    '''

    # TRAIN AND TEST MODELS
    results = [(Classifier_Test_Train(model_type, model_name))]