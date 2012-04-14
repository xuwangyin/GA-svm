#! /usr/bin/env python
# coding=utf-8
        
"""
Find the best gamma and cost combination for svm
"""

import sys
import os
from subprocess import *
import sys
sys.path.append('../')
from pygene.gene import FloatGene, FloatGeneMax
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population

if len(sys.argv) <= 1:
  print('Usage: {0} training_file [testing_file]'.format(sys.argv[0]))
  raise SystemExit

is_win32 = (sys.platform == 'win32')
if not is_win32:
	svmscale_exe = "../linux/svm-scale"
	svmtrain_exe = "../linux/svm-train"
	svmpredict_exe = "../linux/svm-predict"
else:
        # example for windows
	svmscale_exe = r"..\windows\svm-scale.exe"
	svmtrain_exe = r"..\windows\svm-train.exe"
	svmpredict_exe = r"..\windows\svm-predict.exe"

assert os.path.exists(svmscale_exe),"svm-scale executable not found"
assert os.path.exists(svmtrain_exe),"svm-train executable not found"
assert os.path.exists(svmpredict_exe),"svm-predict executable not found"

train_pathname = sys.argv[1]
assert os.path.exists(train_pathname),"training file not found"
file_name = os.path.split(train_pathname)[1]
scaled_file = file_name + ".scale"
model_file = file_name + ".model"
range_file = file_name + ".range"

if len(sys.argv) > 2:
	test_pathname = sys.argv[2]
	file_name = os.path.split(test_pathname)[1]
	assert os.path.exists(test_pathname),"testing file not found"
	scaled_test_file = file_name + ".scale"
	predict_test_file = file_name + ".predict"

cmd = '{0} -s "{1}" "{2}" > "{3}"'.format(svmscale_exe, range_file, train_pathname, scaled_file)
print('Scaling training data...')
Popen(cmd, shell = True, stdout = PIPE).communicate()


class CostExpGene(FloatGene):
    """
    Gene which represents the exponent of cost
    """
    # genes get randomly generated within this range
    randMin = -5
    randMax = 15
    
    # probability of mutation
    mutProb = 0.1
    
    # degree of mutation
    mutAmt = 1


class GammaExpGene(FloatGene):
    """
    Gene which represents the exponent of gamma
    """
    # genes get randomly generated within this range
    randMin = -15
    randMax = 3
    
    # probability of mutation
    mutProb = 0.1
    
    # degree of mutation
    mutAmt = 1


class CostGammaExpOrganism(Organism):
    genome = {'costExp':CostExpGene, 'gammaExp':GammaExpGene}
    fold = 5
    svm_params = ''
    def fitness(self):
        """
        Implements the 'fitness function' for this species.
        """
        #调用svm-train计算交叉验证率        
        cost = 2.0**self['costExp']
        gamma = 2.0**self['gammaExp']

        cmd = '{0} -c {1} -g {2} -v {3} {4} {5}'.format \
          (svmtrain_exe,cost,gamma,self.fold,self.svm_params,scaled_file)
        f = Popen(cmd, shell = True, stdout = PIPE).stdout
        for line in f.readlines():
            if str(line).find("Cross") != -1:
                cross_validation_rate = float(line.split()[-1][0:-1])

        # 个体的fitness越小, 适应性越好, 交叉验证率越高
        fitness = 1.0 - cross_validation_rate / 100.0
        return fitness

    def __repr__(self):
        return "cross_validation_rate=%f cost=%f gamma=%f" % (
            1.0 - self.fitness(), 2.0**self['costExp'], 2.0**self['gammaExp']
            )


class CostGammaExpPopulation(Population):
    initPopulation = 10
    species = CostGammaExpOrganism

def trainPredict(cost, gamma):
    cmd = '{0} -c {1} -g {2} "{3}" "{4}"'.format(svmtrain_exe,cost,gamma,scaled_file,model_file)
    print('Training...')
    Popen(cmd, shell = True, stdout = PIPE).communicate()

    print('Output model: {0}'.format(model_file))
    if len(sys.argv) > 2:
        cmd = '{0} -r "{1}" "{2}" > "{3}"'.format(svmscale_exe, range_file, test_pathname, scaled_test_file)
	print('Scaling testing data...')
	Popen(cmd, shell = True, stdout = PIPE).communicate()	

	cmd = '{0} "{1}" "{2}" "{3}"'.format(svmpredict_exe, scaled_test_file, model_file, predict_test_file)
	print('Testing...')
	Popen(cmd, shell = True).communicate()	

	print('Output prediction: {0}'.format(predict_test_file))


def main():
    pop = CostGammaExpPopulation()
    targetFitness = 0.001
    i = 1
    try:
        print "This is your chance to play God."
        while True:
            print "generation: %d" % i
            b = pop.best()
            print b
            if (b.fitness() <= targetFitness):
                cost = 2.0**b['costExp']
                gamma = 2.0**b['gammaExp']
                trainPredict(cost, gamma)
                break
            i += 1
            pop.gen()
    except KeyboardInterrupt:
        print "current status: "
        print b
        cost = 2.0**b['costExp']
        gamma = 2.0**b['gammaExp']
        trainPredict(cost, gamma)

        
if __name__ == '__main__':
    main()
    
