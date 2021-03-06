from random import randint, random, choice

from algorithm.parameters import params
from representation import individual
from representation.derivation import generate_tree
from utilities.representation.check_methods import check_ind


def mutation(pop):
    """
    Perform mutation on a population of individuals. Calls mutation operator as
    specified in params dictionary.
    
    :param pop: A population of individuals to be mutated.
    :return: A fully mutated population.
    """

    # Initialise empty pop for mutated individuals.
    new_pop = []
    
    # Iterate over entire population.
    for ind in pop:
        
        # Perform mutation.
        new_ind = params['MUTATION'](ind)
        
        # Check ind does not violate specified limits.
        check = check_ind(new_ind, "mutation")
        
        while check:
            # Perform mutation until the individual passess all tests.
            new_ind = params['MUTATION'](ind)
    
            # Check ind does not violate specified limits.
            check = check_ind(new_ind, "mutation")
        
        # Append mutated individual to population.
        new_pop.append(new_ind)
    
    return new_pop


def int_flip_per_codon(ind):
    """
    Mutate the genome of an individual by randomly choosing a new int with
    probability p_mut. Works per-codon. Mutation is performed over the
    effective length (i.e. within used codons, not tails) by default;
    within_used=False switches this off.
    
    :param ind: An individual to be mutated.
    :return: A mutated individual.
    """

    # Set effective genome length over which mutation will be performed.
    if params['WITHIN_USED']:
        eff_length = min(len(ind.genome), ind.used_codons)
    else:
        eff_length = len(ind.genome)

    # Set mutation probability. Default is 1 over the length of the genome.
    if params['MUTATION_PROBABILITY'] and params['MUTATION_EVENTS'] == 1:
        p_mut = params['MUTATION_PROBABILITY']
    elif params['MUTATION_PROBABILITY'] and params['MUTATION_EVENTS'] > 1:
        s = "operators.mutation.int_flip_per_codon\n" \
            "Error: mutually exclusive parameters for 'MUTATION_PROBABILITY'" \
            "and 'MUTATION_EVENTS' have been explicitly set.\n" \
            "       Only one of these parameters can be used at a time with" \
            "int_flip_per_codon mutation."
        raise Exception(s)
    else:
        # Default mutation events per individual is 1. Raising this number
        # will influence the mutation probability for each codon.
        p_mut = params['MUTATION_EVENTS']/eff_length

    # Mutation probability works per-codon over the portion of the
    # genome as defined by the within_used flag.
    for i in range(eff_length):
        if random() < p_mut:
            ind.genome[i] = randint(0, params['CODON_SIZE'])

    # Re-build a new individual with the newly mutated genetic information.
    new_ind = individual.Individual(ind.genome, None)

    return new_ind


def int_flip_per_ind(ind):
    """
    Mutate the genome of an individual by randomly choosing a new int with
    probability p_mut. Works per-individual. Mutation is performed over the
    entire length of the genome by default, but the flag within_used is
    provided to limit mutation to only the effective length of the genome.
    
    :param ind: An individual to be mutated.
    :return: A mutated individual.
    """
    
    # Set effective genome length over which mutation will be performed.
    if params['WITHIN_USED']:
        eff_length = min(len(ind.genome), ind.used_codons)
    else:
        eff_length = len(ind.genome)
    
    for _ in params['MUTATION_EVENTS']:
        idx = randint(0, eff_length-1)
        ind.genome[idx] = randint(0, params['CODON_SIZE'])
    
    # Re-build a new individual with the newly mutated genetic information.
    new_ind = individual.Individual(ind.genome, None)

    return new_ind
    

def subtree(ind):
    """
    Mutate the individual by replacing a randomly selected subtree with a
    new randomly generated subtree. Guaranteed one event per individual, unless
    params['MUTATION_EVENTS'] is specified as a higher number.
    
    :param ind: An individual to be mutated.
    :return: A mutated individual.
    """

    def subtree_mutate(ind_tree):
        """
        Creates a list of all nodes and picks one node at random to mutate.
        Because we have a list of all nodes, we can (but currently don't)
        choose what kind of nodes to mutate on. Handy.

        :param ind_tree: The full tree of an individual.
        :return: The full mutated tree and the associated genome.
        """
    
        # Find the list of nodes we can mutate from.
        targets = ind_tree.get_target_nodes([], target=params[
                                          'BNF_GRAMMAR'].non_terminals)
        
        # Pick a node.
        new_tree = choice(targets)

        # Set the depth limits for the new subtree.
        if params['MAX_TREE_DEPTH']:
            # Set the limit to the tree depth.
            max_depth = params['MAX_TREE_DEPTH'] - new_tree.depth
        
        else:
            # There is no limit to tree depth.
            max_depth = None
    
        # Mutate a new subtree.
        generate_tree(new_tree, [], [], "random", 0, 0, 0, max_depth)
    
        return ind_tree

    # Save the tail of the genome.
    tail = ind.genome[ind.used_codons:]
    
    # Allows for multiple mutation events should that be desired.
    for i in range(params['MUTATION_EVENTS']):
        ind.tree = subtree_mutate(ind.tree)
    
    # Re-build a new individual with the newly mutated genetic information.
    ind = individual.Individual(None, ind.tree)
    
    # Add in the previous tail.
    ind.genome = ind.genome + tail

    return ind


# Set attributes for all operators to define linear or subtree representations.
int_flip_per_codon.representation = "linear"
int_flip_per_ind.representation = "linear"
subtree.representation = "subtree"
