import numpy as np
from sklearn.utils import shuffle

def create_minibatches(X, Y, minibatch_size):
    shuffled_X, shuffled_Y = shuffle(X, Y)
    complete_batches = X.shape[0] // minibatch_size
    mini_batches = []
    for i in range(0, minibatch_size*complete_batches+1, minibatch_size):
        if i == minibatch_size*complete_batches:
            mini_x, mini_y = shuffled_X[i:,:], shuffled_Y[i:,:]
        else:
            mini_x, mini_y = shuffled_X[i: i+minibatch_size,:], shuffled_Y[i:i+minibatch_size,:]
        mini_batches.append((mini_x, mini_y))
    return mini_batches

def initialize_parameters(layers_dims):
    L = len(layers_dims)
    parameters ={}
    for l in range(1, L):
        parameters[f'W{l}'] = np.random.randn(layers_dims[l-1], layers_dims[l]) * np.sqrt(2 / layers_dims[l-1])
        parameters[f'b{l}'] = np.zeros((1, layers_dims[l]))
    return parameters

def relu(Z):
    return np.maximum(Z,0)

def softmax(Z):
    expZ = np.exp(Z)
    return expZ / (expZ.sum(axis=1, keepdims=True) + 1e-8)

def sigmoid(Z):
    return 1 / (1 + np.exp(-Z) + 1e-8)

def relu_derivative(A):
    return np.where(A<=0, 0, 1)

def forward(X, parameters, classification):
    L = len(parameters)//2
    activations = {'A0':X}
    for l in range(1, L):
        activations[f'A{l}'] = relu(activations[f'A{l-1}'].dot(parameters[f'W{l}']) + parameters[f'b{l}'])
    if classification == 'binary':
        activations[f'A{L}'] = sigmoid(activations[f'A{L-1}'].dot(parameters[f'W{L}']) + parameters[f'b{L}'])
    elif classification == 'multiclass':
        activations[f'A{L}'] = softmax(activations[f'A{L-1}'].dot(parameters[f'W{L}']) + parameters[f'b{L}'])
    return activations


def safeLog(data):
  min_nonzero = np.min(data[np.nonzero(data)])
  data[data == 0] = min_nonzero
  return data

def cost(Y, Yhat, classification, parameters, lambd):
    n = Yhat.shape[0]
    l2 = 0
    for l in range(1,(len(parameters)//2) + 1):
        l2 += np.sum(np.square(parameters[f'W{l}']))

    if classification == 'binary':
        return (-1/n)*((Y*np.log(safeLog(Yhat)) + (1-Y)*np.log(1-Yhat)).sum()) + (lambd / (2*n))*l2
    elif classification == 'multiclass':
        return (-1/n)*((Y*np.log(safeLog(Yhat))).sum())  + (lambd / (2*n))*l2

def accuracy(Y, Yhat, classification):
    n_total = Y.shape[0]
    if classification == 'binary':
        Yhat = np.round(Yhat)
    elif classification == 'multiclass':
        Yhat = np.argmax(Yhat, axis=1)
        Y = np.argmax(Y, axis=1)
    n_correct = 0
    for i in range(n_total):
        if Yhat[i] == Y[i]:
            n_correct += 1
    return n_correct / n_total

def initialize_adam(parameters):
    L = len(parameters) // 2
    v = {}
    s = {}
    for l in range(1,L+1):
        v[f'dW{l}'] = np.zeros(parameters[f'W{l}'].shape)
        v[f'db{l}'] = np.zeros(parameters[f'b{l}'].shape)
        s[f'dW{l}'] = np.zeros(parameters[f'W{l}'].shape)
        s[f'db{l}'] = np.zeros(parameters[f'b{l}'].shape)
    return v, s

def update_parameters_with_adam(parameters, activations, Y, v, s, t, learning_rate, lambd, beta1, beta2, epsilon):
    L =len(parameters) // 2
    N = Y.shape[0]
    errors = {f'dZ{L}' : (activations[f'A{L}'] - Y)/N}
    grads = {}
    v_corrected = {}
    s_corrected = {}
    for l in range(L, 0, -1):
        grads[f'dW{l}'] = activations[f'A{l-1}'].T.dot(errors[f'dZ{l}'])
        grads[f'db{l}'] = errors[f'dZ{l}'].sum(axis=0)
        v[f'dW{l}'] = beta1*v[f'dW{l}'] + (1-beta1)*grads[f'dW{l}']
        v[f'db{l}'] = beta1*v[f'db{l}'] + (1-beta1)*grads[f'db{l}']
        
        v_corrected[f'dW{l}'] = v[f'dW{l}'] / (1 - np.power(beta1, t))
        v_corrected[f'db{l}'] = v[f'db{l}'] / (1 - np.power(beta1, t))
        
        s[f'dW{l}'] = beta2*s[f'dW{l}'] + (1-beta2)*np.square(grads[f'dW{l}'])
        s[f'db{l}'] = beta2*s[f'db{l}'] + (1-beta2)*np.square(grads[f'db{l}'])

        s_corrected[f'dW{l}'] = s[f'dW{l}'] / (1 - np.power(beta2, t))
        s_corrected[f'db{l}'] = s[f'db{l}'] / (1 - np.power(beta2, t))
        
        parameters["W" + str(l)] -=   learning_rate*((v_corrected['dW' + str(l)] / (np.sqrt(s_corrected['dW' + str(l)]) + epsilon)) + (lambd*parameters[f'W{l}'])/N)
        parameters["b" + str(l)] -=   learning_rate*(v_corrected['db' + str(l)] / (np.sqrt(s_corrected['db' + str(l)]) + epsilon))
        
        errors[f'dZ{l-1}'] = (errors[f'dZ{l}'].dot(parameters[f'W{l}'].T))*relu_derivative(activations[f'A{l-1}'])
    return parameters

def train(X_train, Y_train, X_test, Y_test, layers_dims, classification, learning_rate, epochs, lambd=0, beta1=0.9, beta2=0.999,epsilon = 1e-8):
    train_costs = []
    test_costs = []
    parameters = initialize_parameters(layers_dims)
    L = len(parameters) // 2
    v, s = initialize_adam(parameters)
    t = 1
    
    for i in range(epochs):
        train_activation_cache = forward(X_train, parameters, classification)
        test_activation_cache = forward(X_test, parameters, classification)
        if i % 10 == 0:
            Yhat_train = train_activation_cache[f'A{L}']
            Yhat_test = test_activation_cache[f'A{L}']
            c_train = cost(Y_train, Yhat_train, classification, parameters, lambd)
            a_train = accuracy(Y_train, Yhat_train, classification)
            c_test = cost(Y_test, Yhat_test, classification, parameters, lambd)
            a_test = accuracy(Y_test, Yhat_test, classification)
            train_costs.append(c_train)
            test_costs.append(c_test)
                
        parameters = update_parameters_with_adam(parameters,train_activation_cache,Y_train, v, s, t, learning_rate, lambd, beta1, beta2, epsilon)
        t += 1
        
    return parameters

def train_minibatch(X_train, Y_train, X_test, Y_test, layers_dims, classification, learning_rate, epochs, batch, lambd=0, beta1=0.9, beta2=0.999,epsilon = 1e-8):
    train_costs = []
    test_costs = []
    parameters = initialize_parameters(layers_dims)
    v, s = initialize_adam(parameters)
    L = len(parameters) // 2
    t = 1
    for i in range(epochs):
        mini_batches = create_minibatches(X_train, Y_train, batch) 
        cst = 0
        for minibatch in mini_batches:
            X_mini, Y_mini = minibatch
            train_activation_cache = forward(X_mini, parameters, classification)
            Yhat = train_activation_cache[f'A{L}']
            parameters = update_parameters_with_adam(parameters,train_activation_cache,Y_mini, v, s, t, learning_rate, lambd, beta1, beta2, epsilon)
            t += 1
        train_activation_cache = forward(X_train, parameters, classification)
        test_activation_cache = forward(X_test, parameters, classification)
        if i % 10 == 0:
            Yhat_train = train_activation_cache[f'A{L}']
            Yhat_test = test_activation_cache[f'A{L}']
            c_train = cost(Y_train, Yhat_train, classification, parameters, lambd)
            a_train = accuracy(Y_train, Yhat_train, classification)
            c_test = cost(Y_test, Yhat_test, classification, parameters, lambd)
            a_test = accuracy(Y_test, Yhat_test, classification)
            train_costs.append(c_train)
            test_costs.append(c_test)

            if i % 10 == 0:
                print(f' epoch : {i}, train cost : {c_train}, test_cost : {c_test}, training accuracy : {a_train}, testing accuracy : {a_test}')

    return {"parameters": parameters, "train_cost" : train_costs, "test_cost" : test_costs, "a_train" : a_train, "a_test" : a_test}

def predict(X, parameters, classification):
    activation_cache = forward(X, parameters, classification)
    L = len(parameters) // 2
    Yhat = activation_cache[f'A{L}']

    return Yhat