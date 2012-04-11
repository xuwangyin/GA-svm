#! /usr/bin/env python
# coding=utf-8
        
import sys
import os
from subprocess import *

if len(sys.argv) <= 1:
  print('Usage: {0} training_file [testing_file]'.format(sys.argv[0]))
  raise SystemExit

is_win32 = (sys.platform == 'win32')
if not is_win32:
	svmscale_exe = "../svm-scale"
	svmtrain_exe = "../svm-train"
	svmpredict_exe = "../svm-predict"
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

"""
Find the best gamma and cost combination for svm
"""

from pygene.gene import FloatGene, FloatGeneMax
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population

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


pop = CostGammaExpPopulation()
targetFitness = 0.001

def main():
    i = 1
    try:
        print "This is your chance to play God."
        while True:
            print "generation: %d" % i
            b = pop.best()
            print b
            if (b.fitness() <= targetFitness):
                break
            i += 1
            pop.gen()
    except KeyboardInterrupt:
        print "current status: "
        print b

        
if __name__ == '__main__':
    main()        
