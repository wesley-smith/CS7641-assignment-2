"""
SA NN training on Madelon data (Feature selection complete)

"""
import os
import csv
import time
import sys
sys.path.append("/Users/wessm/OMSCS/ML/CS-7641-assignment-2/ABAGAIL/ABAGAIL.jar")
from func.nn.backprop import BackPropagationNetworkFactory
from shared import SumOfSquaresError, DataSet, Instance
from opt.example import NeuralNetworkOptimizationProblem
from func.nn.backprop import RPROPUpdateRule, BatchBackPropagationTrainer
import opt.RandomizedHillClimbing as RandomizedHillClimbing
import opt.SimulatedAnnealing as SimulatedAnnealing
import opt.ga.StandardGeneticAlgorithm as StandardGeneticAlgorithm
from func.nn.activation import RELU

# Network parameters found "optimal" in Assignment 1
INPUT_LAYER = 104
HIDDEN_LAYER_1 = 100
HIDDEN_LAYER_2 = 100
OUTPUT_LAYER = 1
TRAINING_ITERATIONS = 2001
OUTFILE = './NN_OUTPUT/XXX_LOG.txt'


def initialize_instances(infile):
    """Read the m_trg.csv CSV data into a list of instances."""
    instances = []

    # Read in the CSV file
    with open(infile, "r") as dat:
        reader = csv.reader(dat)

        for row in reader:
            instance = Instance([float(value) for value in row[:-1]])
            instance.setLabel(Instance(float(row[-1])))
            instances.append(instance)

    return instances


def errorOnDataSet(network,ds,measure):
    N = len(ds)
    error = 0.
    correct = 0
    incorrect = 0
    # following to calculate balanced accuracy
    total_0 = 0.
    correct_0 = 0.
    total_1 = 0.
    correct_1 = 0.
    for instance in ds:
        network.setInputValues(instance.getData())
        network.run()
        actual = instance.getLabel().getContinuous()
        predicted = network.getOutputValues().get(0)
        predicted = max(min(predicted,1),0)
        if abs(predicted - actual) < 0.5:
            correct += 1
            if actual == 0.:
                total_0 += 1
                correct_0 += 1
            else:
                total_1 += 1
                correct_1 += 1
        else:
            incorrect += 1
            if actual == 0.:
                total_0 += 1
            else:
                total_1 += 1
        output = instance.getLabel()
        output_values = network.getOutputValues()
        example = Instance(output_values, Instance(output_values.get(0)))
        error += measure.value(output, example)
    MSE = error/float(N)
    # Balanced accuracy calculation
    # acc = correct/float(correct+incorrect)
    acc = 0.5*(correct_0/total_0 + correct_1/total_1)

    return MSE,acc
	
	
def train(oa, network, oaName, training_ints,validation_ints,testing_ints, measure):
    """Train a given network on a set of instances.
    """
    print "\nError results for %s\n---------------------------" % (oaName,)
    times = [0]
    it = 0
    for iteration in xrange(TRAINING_ITERATIONS):
        print it
        it += 1
        start = time.clock()
        oa.train()
        elapsed = time.clock()-start
    	times.append(times[-1]+elapsed)
        if iteration % 10 == 0:
    	    MSE_trg, acc_trg = errorOnDataSet(network,training_ints,measure)
            MSE_val, acc_val = errorOnDataSet(network,validation_ints,measure)
            MSE_tst, acc_tst = errorOnDataSet(network,testing_ints,measure)
            txt = '{},{},{},{},{},{},{},{}\n'.format(iteration,MSE_trg,MSE_val,MSE_tst,acc_trg,acc_val,acc_tst,times[-1]);print txt
            with open(OUTFILE.replace('XXX',oaName),'a+') as f:
                f.write(txt)

def main(P,mate,mutate):
    """Run this experiment"""
    training_ints = initialize_instances('m_trg.csv')
    testing_ints = initialize_instances('m_test.csv')
    validation_ints = initialize_instances('m_val.csv')
    factory = BackPropagationNetworkFactory()
    measure = SumOfSquaresError()
    data_set = DataSet(training_ints)
    relu = RELU()
    rule = RPROPUpdateRule()
    oa_name = "GA_{}_{}_{}".format(P,mate,mutate)
    with open(OUTFILE.replace('XXX',oa_name),'w') as f:
        f.write('{},{},{},{},{},{},{},{}\n'.format('iteration','MSE_trg','MSE_val','MSE_tst','acc_trg','acc_val','acc_tst','elapsed'))
    classification_network = factory.createClassificationNetwork([INPUT_LAYER, HIDDEN_LAYER_1, HIDDEN_LAYER_2, OUTPUT_LAYER],relu)
    nnop = NeuralNetworkOptimizationProblem(data_set, classification_network, measure)
    oa = StandardGeneticAlgorithm(P, mate, mutate, nnop)
    train(oa, classification_network, oa_name, training_ints,validation_ints,testing_ints, measure)
        


if __name__ == "__main__":
    # for p in [50]:
    #     for mate in [20,10]:
    #         for mutate in [20,10]:
    p = 50
    mate = 10
    mutate = 20
    args = (p,mate,mutate)
    main(*args)

