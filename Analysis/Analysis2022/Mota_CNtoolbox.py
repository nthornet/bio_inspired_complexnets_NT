# Neural Pathways Laboratory #
# University of Sheffield - University of Brazil (Federal University of Rio de Janeiro) #

# Toolbox for relevant metric-extraction from biologically inspired complex networks #

# ----------------------------------------------------------------------------------------------------------------- #

# Written by Dr Rodrigo Kazu #
# Any enquiries to r.siqueiradesouza@sheffield.ac.uk #

# ----------------------------------------------------------------------------------------------------------------- #

from igraph import *
from pandas import *

import numpy as np
import time
import threading



# ----------------------------------------------------------------------------------------------------------------- #
# Data analysis #
# ----------------------------------------------------------------------------------------------------------------- #


def analyse_50nets(fiftynets, exportpath):

    """ Runs the analysis for the networks modelled at 50k neurons density and export results;
        This function initiates all the threads and run the analysis in parallel for the same network;
        The .join() function guarantees that all threads will finish at the same time

             Arguments:

                 fiftynets(list): Path for the networks to be analysed generated with the network_acquisition() function
                  of this toolbox.

           Returns:

              Exported complex network statistics.

|   """

    t1 = threading.Thread(target=parallel_cluster_50k, args=(fiftynets,exportpath))
    t2 = threading.Thread(target=parallel_averagepath_50k, args=(fiftynets, exportpath))
    t3 = threading.Thread(target=parallel_shortestpath_50k, args=(fiftynets,))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()


def network_acquisition(density_path):

    """ Acquires the paths to the biologically-inspired networks for further analysis

          Arguments:

              density_path(str): Paths to the directory where the networks of correct density are stored

        Returns:

           Networks path and list containing all the network files

        """

    paths = density_path  # A list with the Sim folders "Sim 1", "Sim 2", etc.


    all_sims = dict()

    for path in paths:

        edges_path = path + "\\Edges\\"  # This is the folder structure chosen

        nets = os.listdir(edges_path)  # Obtains all the files in the folder.
        net_paths = list()

        for net in nets:

            network_file = edges_path + net
            net_paths.append(network_file)

        if path[-5] == "S":

            all_sims[path[-5:]] = net_paths

        else:

            all_sims[path[-6:]] = net_paths

    return all_sims


def network_density_paths(main_path):

    """ Acquires the paths to the biologically-inspired networks of 100k and 50k densities for further analysis

             Arguments:

                 main_path(str): Paths to the directory where the networks are stored

           Returns:

              Networks paths for 50k and 100k density simulations
             """

    fifty = main_path + "\\50k\\"
    hundred = main_path + "\\100k\\"

    fiftysims = os.listdir(fifty)
    hundredsims = os.listdir(hundred)

    fiftysims_paths = list()
    hundredsims_paths = list() # To export a list with the Sim folders "Sim 1", "Sim 2", etc.

    for sim in fiftysims:

        path = fifty + sim
        fiftysims_paths.append(path)

    for sim in hundredsims:

        path = hundred + sim
        hundredsims_paths.append(path)

    return fiftysims_paths, hundredsims_paths


def parallel_averagepath_50k(fiftynets, exportpath):

    """ Computes the average path length for a list of networks generated with network_acquisition()

      Arguments:

          fiftynets(list): List of networks generated with network_acquisition()
          exportpath(str): Path to export the dataset as a csv

           Returns:

            Average path exported as csv

        """

    averagepaths = dict()
    netnumbers = list()

    for Sim in fiftynets:  # Fifty nets is a dict with Sims as keys

        averagepaths[Sim] = dict()

        for nets in fiftynets[Sim]:

            print("Average path calculations for ", nets)

            net = Graph.Read(nets)

            net_vcount = net.vcount()
            net_ecount = net.ecount()

            print("Nodes:", net_vcount)
            print("Edges:", net_ecount)

            print(f"[Path calculation started]")
            print(f"[Calculating average path length on thread number ] {threading.current_thread()}")
            path = net.average_path_length()  # Target is what's running on the new thread

            print(f'The average path length is {path}')

            label = network_labelling(nets)
            name = "AveragePath.csv"

            averagepaths[Sim][label[0]] = path

            write_metrics(metric=averagepaths, exportpath=exportpath, name=name)

    return averagepaths


def parallel_cluster_50k(fiftynets, exportpath):

    """ Computes the clustering coefficient for a list of networks generated with network_acquisition()

                 Arguments:

                     fiftynets(list): List of networks generated with network_acquisition()
                     exportpath(str): Path to export the dataset as a csv

               Returns:

                Clustering coefficients exported as csv

   """

    averagecluster = dict()

    for Sim in fiftynets:  # Fifty nets is a dict with Sims as keys

        averagecluster[Sim] = dict()

        for nets in fiftynets[Sim]:

            print("Clustering calculations for ", nets)
            net = Graph.Read(nets)

            net_vcount = net.vcount()
            net_ecount = net.ecount()

            print("Nodes:", net_vcount)
            print("Edges:", net_ecount)

            print(f"[Cluster calculation started]")
            print(f"[Calculating transitivity on thread number ] {threading.current_thread()}")
            clustering = net.transitivity_undirected()  # Target is what's running on the new thread
            print(f'The clustering coefficient is {clustering}')

            label = network_labelling(netpath=nets)
            name = "AverageClustering.csv"

            averagecluster[Sim][label[0]] = clustering

            write_metrics(metric=averagecluster, exportpath=exportpath, name=name)

    return averagecluster


def parallel_shortestpath_50k(fiftynets):

    """ Computes the shortest path length for a list of networks generated with network_acquisition()

                 Arguments:

                     fiftynets(list): List of networks generated with network_acquisition()

               Returns:

                  Shortest path length

   """

    for Sim in fiftynets:  # Fifty nets is a dict with Sims as keys

        for nets in fiftynets[Sim]:

            print("Shortest path calculations for ", nets)

            net = Graph.Read(nets)

            net_vcount = net.vcount()
            net_ecount = net.ecount()

            print("Nodes:", net_vcount)
            print("Edges:", net_ecount)

            start = time.perf_counter()
            print(f"[Path calculation started]")
            print(f"[Calculating average path length on thread number ] {threading.current_thread()}")
            path = np.mean(net.shortest_paths())

            finish = time.perf_counter()
            print(f'Finished in {round(finish - start, 2)} seconds (s) and the shortest path length is {path}')

    return path


def write_metrics(metric, exportpath, name):

    """ Writes the results of the analysis for the networks modelled at 50k neurons density and export results;


         Arguments:

             averagepath(list): Dataset containing the average path length for the networks analysed

       Returns:

          Exported complex network statistics.

|   """

    df = DataFrame(data=metric)
    # df['Net number'] = label[1]
    file = exportpath + name
    df.to_csv(file)

    return statistics


# ----------------------------------------------------------------------------------------------------------------- #
# Support functions #
# ----------------------------------------------------------------------------------------------------------------- #


def network_labelling(netpath):

    """ Support function to properly label the networks in the dataframes and in the exports

             Arguments:

                 netpath(str):Path of the network

           Returns:

              Label (str)

           """

    char = -8
    counter = 1

    while netpath[char].isdigit() == True:

        char = char - 1
        counter = counter + 1

    if char == -8:

        if netpath[char] == "h":

            label = "death"+netpath[-7]

            return label, netpath[-7]

        else:

            label = "pruning"+netpath[-7]

            return label, netpath[-7]

    else:

        counter = counter * -1
        start = -6 + counter  # Playing with slicing

        if netpath[char] == "h":

            label = "death" + netpath[start:-6]

            return label, netpath[start:-6]

        else:

            label = "pruning" + netpath[start:-6]

            return label, netpath[start:-6]
