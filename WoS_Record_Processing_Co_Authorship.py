###WRITTEN BY DERYC T. PAINTER
###SEPT. 17TH, 2019

import itertools as it
import networkx as nx
from networkx.algorithms import approximation as approx
from scipy.sparse.linalg import svds, eigs

###TAKE CARE TO ENTER THE FOLLOWING USER INPUTS CAREFULLY.
###THE SCRIPT WILL NOT RUN IF THEY ARE ENTERED INCORRECTLY

University = input('Enter the title of this project (i.e. Arizona_State_Records): ')

userFile = input('Enter the full name, including the full path, of the Web of Science record you wish to analyze (i.e. /Users/savedrecs.txt): ')

userYearStart = input('Enter the first year you wish to analyze (i.e. 1995): ')
userYearEnd = input('Enter the last year you wish to analyzed (i.e. 2015): ')


###DO NOT INCLUDE THE '/' AFTER THE PATH
userPathStats = input('Enter the path where the statistics file will be saved (i.e. /Users): ')
userPathGraphs = input('Enter the path where the network graphs will be saved (i.e. /Users): ')

statsfile = open(r''+userPathStats+'/Stats_'+University+'.txt','w')
print('YEAR\tRECORDS\tNODES\tEDGES\tDENSITY\tDEGREE ASSORT COEFF\tAVG CLUSTER COEFF\tDEGREE OF FRAGMENTATION\tNUMBER OF CLIQUES\tSVDs',file=statsfile)

year = range(int(userYearStart),int(userYearEnd+1))

###CREATE THE EDGE LIST FOR EACH PUBLICATION
###ADDS EACH EDGE FROM THE EDGE LIST TO THE GRAPH OBJECT
###THIS IS DONE ONE EDGE AT A TIME TO MINIMIZE COMPUTER RAM USAGE
###PREVENTS MEMORY ERRORS FOR VERY LARGE GRAPHS

for i in year:
  authors_collab_year = []
  print('Beginning to Process '+str(i)+'.')
  with open(r''+userFile,'r',encoding='utf-8-sig') as f1:
    G = nx.Graph()
    G.clear()
    count = 0
    this_year = ''
    that_year = str(i)
    for line in f1:
      line = line.split('\t')
      this_year = line[44]
      if this_year == that_year:
        count += 1
        authors = line[1].split(';')
        if len(authors) > 1:
          authors_collab_record = []
          authors_collab_record = it.combinations(authors,2)
          for j,k in authors_collab_record:
            G.add_edge(j,k)
            if G.number_of_edges() % 10000 == 0:
              print('{} edges were added to graph object.'.format(G.number_of_edges()))
        if count % 100 == 0:
          print('{} records from {} have been processed.'.format(count,that_year))          
              
  print(that_year+' has {} records.'.format(count))

  nodecnt = G.number_of_nodes()
  edgecnt = G.number_of_edges()
  
  print('{} has {} nodes in its network.'.format(that_year,nodecnt))
  print('{} has {} edges in its network.'.format(that_year,edgecnt))

  ###GRAPH DENSITY
  den = nx.density(G)
  print('{} has a density of {}.'.format(that_year,round(den,5)))

  ###DEGREE ASSORTATIVITY
  deg_assort = nx.degree_assortativity_coefficient(G)
  print('{} has a degree assortativity of {}.'.format(that_year,round(deg_assort,5)))
  
  ###APPROXIMATE AVERAGE CLUSTERING COEFFICIENT###
  avg_clust = approx.average_clustering(G,trials=10000)
  print('{} has an average clustering of {}.'.format(that_year,avg_clust))


  ###DEGREE OF FRAGMENTATION--BORGATTI'S KEY PLAYER PROBLEM###
  denominator = nodecnt*(nodecnt-1)
  sum_of_distance = 0.0
  distance_matrix = nx.all_pairs_shortest_path_length(G)
  for source, destinations in distance_matrix:
    for destination, length in destinations.items():
      if not source == destination:
        sum_of_distance += 1 / length
  degree_of_fragmentation = (2 * sum_of_distance) / denominator
  print('{} has a degree of fragmentation of {}.'.format(that_year,degree_of_fragmentation))

  ###NUMBER OF CLIQUES###
  num_of_cliques = nx.graph_number_of_cliques(G)
  print('{} has {} cliques.'.format(that_year,num_of_cliques))

  ###SINGULAR VALUE DECOMPOSITION###
  adj_matrix = nx.adjacency_matrix(G)
  adj_matrix = adj_matrix.astype(float)
  u, s, vt = svds(adj_matrix, k=2)
  print('The SVD of {} is {}.'.format(that_year,s))
  
  print('Writing GML file.')
  nx.write_gml(G, r''+userPathGraphs+'/CoAuthorship_'+that_year+University+'.gml')
  print('Writing Pajek file.')
  nx.write_pajek(G, r''+userPathGraphs+'/CoAuthorship_'+that_year+University+'.net')

  print('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{},{}'.format(that_year,count,nodecnt,edgecnt,den,deg_assort,avg_clust,degree_of_fragmentation,num_of_cliques,s[0],s[1]),file=statsfile)

statsfile.close()
