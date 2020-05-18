#------------------------------------------------
#
#  Alexander Cooper
#  alec.n.cooper@gmail.com
#
#------------------------------------------------
import torch.optim as optim
import torch as torch
import torch.nn.functional as func
import numpy as np
import lang_model as model
import data_parse as parser
import json
import os
import matplotlib.pyplot as plt

# Main training loop
def train(hyper):

    # Load in our dataset
    data = parser.Data(hyper["file location"],10,True,10000)

    # Create our model
    net = model.Net(data.x_train.size()[0])

    # Extract learning rate from hyper parameters
    lr=hyper["learning rate"]

    # Create our optimizer
    optimizer = optim.Adam(net.parameters(), lr)

    # Create our loss function
    loss_func = torch.nn.BCELoss(reduction="mean")

    # Extract num epochs from hyper parameters
    num_epochs = hyper["num_epochs"]

    # list of our training loss values
    loss_vals = []
    
    # lists to track preformance of network
    obj_vals= []
    cross_vals= []
    correct_vals = []

    # Training loop
    for epoch in range(1,num_epochs+1):

        # Clear our gradient buffer
        optimizer.zero_grad()

        # Clear our gradients
        net.zero_grad

        # Feed the output throught the net
        output = net.forward(data.x_train)

        # calculate loss function
        loss = loss_func(output[:,0],data.y_train)
        loss_vals.append(loss)

        # Backpropagate the loss
        loss.backward()

        # Calculate test data
        test_data = net.test(data, loss_func, epoch)
        test_val = test_data[0]
        test_output = test_data[1]

        # Calc percent correct
        i = 0
        num_correct = 0
        for choice in test_output:
            if choice < 0.5 and data.y_test[i] < 0.5:
                num_correct += 1
            elif choice > 0.5 and data.y_test[i] > 0.5:
                num_correct += 1
            i+=1
        pecent_correct = num_correct/len(data.y_test) * 100.0

        # Graph our progress
        obj_vals.append(loss)
        cross_vals.append(test_val)
        correct_vals.append(pecent_correct)

        optimizer.step()

        # High verbosity report in output stream
        if hyper["verbosity"] >=2:
            if not ((epoch + 1) % hyper["display epochs"]):
                print('Epoch [{}/{}]'.format(epoch, num_epochs) +\
                    '\tTraining Loss: {:.4f}'.format(loss) +\
                    '\tTest Loss: {:.4f}'.format(test_val) +\
                    "\tPercent Correct: {:.2f}".format(pecent_correct) +\
                        "%")
    
    # Low verbosity final report
    if hyper["verbosity"]:
        print('Final training loss: {:.4f}'.format(obj_vals[-1]))
        print('Final test loss: {:.4f}'.format(cross_vals[-1]))

    # Plot Results
    plt.plot(range(num_epochs), obj_vals, label= "Training loss", color="blue")
    plt.plot(range(num_epochs), cross_vals, label= "Test loss", color= "green")
    plt.ylabel("Binary Cross Entropy Loss")
    plt.xlabel("Training Epoch")
    plt.legend()
    plt.savefig("Training-Test-Loss")
    plt.show()

if  __name__ == "__main__":

    # TEMP: location of paramater file
    p_file = "/Users/aleccooper/Documents/Translate/Detection/hyper.json"

    # import hyper parameters
    with open(p_file) as paramfile:
        hyper = json.load(paramfile)

    # We need to check if the data parser has run on the corpus yet
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isfile(dir_path + "/Data/x_test.npy"):
        data = parser.Data(hyper["file location"],10,False,5)

    train(hyper)


    
    