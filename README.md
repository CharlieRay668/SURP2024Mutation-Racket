The code in this repository has an extrordinary amout of technical debt, I am sorry. This repo is basically a collection of scripts (bash or python) that all work together to build a pipeline for Mutation analysis on racket projects.
The primary file that actually runs mutation analysis is mutation-tester.rkt, the following mutators are defined within this file:
aod-add (Arithmetic Deletion Operator, Addition)
Mutates (+ 1 2 3) into three mutatns, 1, 2, or 3. Mutates (+ j_1 j_2 ... j_n) into n mutatns, j_i for all 1<=i<=n
aod-minus (Arithmetic Deletion Operator, Subtraction)
Mutates (- 1 2 3) into three mutatns, 1, 2, or 3. Mutates (- j_1 j_2 ... j_n) into n mutatns, j_i for all 1<=i<=n
aod-mul (Arithmetic Deletion Operator, Multiplication)
Mutates (* 1 2 3) into three mutatns, 1, 2, or 3. Mutates (* j_1 j_2 ... j_n) into n mutatns, j_i for all 1<=i<=n
aod-div (Arithmetic Deletion Operator, Division)
Mutates (/ 1 2 3) into three mutatns, 1, 2, or 3. Mutates (/ j_1 j_2 ... j_n) into n mutatns, j_i for all 1<=i<=n
aod-mod (Arithmetic Deletion Operator, Modulo)
Mutates (modulo 1 2 3) into three mutatns, 1, 2, or 3. Mutates (modulo j_1 j_2 ... j_n) into n mutatns, j_i for all 1<=i<=n
RC-and->false (Remove Conditionals, insert false into and)
Mutates (and x y z) into three mutants. (and #f y z), (and x #f z) (and x y #f). Mutates (and j_i j_2 ... j_n) into n mutatns where one j_i is replaced with #f
RC-and->true (Remove Conditionals, insert true into and)
Mutates (and x y z) into three mutants. (and #t y z), (and x #t z) (and x y #t). Mutates (and j_i j_2 ... j_n) into n mutatns where one j_i is replaced with #t
RC-or->false (Remove Conditionals, insert false into or)
Mutates (or x y z) into three mutants. (or #f y z), (or x #f z) (or x y #f). Mutates (or j_i j_2 ... j_n) into n mutatns where one j_i is replaced with #f
RC-or->true (Remove Conditionals, insert true into or)
Mutates (or x y z) into three mutants. (or #t y z), (or x #t z) (or x y #ft). Mutates (or j_i j_2 ... j_n) into n mutatns where one j_i is replaced with #t
RC-cond->false (Remove Conditionals, insert false into cond
Mutats (cond [x 3] [y 3] [else 4]) into  three mutants. (cond [#f 3] [y 3] [else 4]) (cond [x 3] [#f 3] [else 4]) (cond [x 3] [y 3] [#f 4]) mutates (cond [j_1 foo] ... [j_n foo]) into n mutatns where one j_i is replaced with #f
RC-cond->true (Remove Conditionals, insert true into cond
Mutats (cond [x 3] [y 3] [else 4]) into  three mutants. (cond [#t 3] [y 3] [else 4]) (cond [x 3] [#t 3] [else 4]) (cond [x 3] [y 3] [#t 4]) mutates (cond [j_1 foo] ... [j_n foo]) into n mutatns where one j_i is replaced with #t
RC-if->false (Remove Conditionals, force if else branch)
Mutates (if cond then else) into one mutant, just the else branch (else)
RC-if->true (Remove Conditionals, force if then branch)
Mutates (if cond then else) into one mutant, just the then branch (then)
RC-match-removal (Remove Conditionals, remove one match branch)
Mutats (match [cond_1 then] [cond_2 then] [cond_3 then]) into three mutants (match [cond_2 then] [cond_3 then]) (match [cond_1 then] [cond_3 then]) (match [cond_1 then] [cond_2 then]) mutates (match [cond_1 then] ... [cond_n then]) into n mutants where one cond_i branch is removed

mutation-tester.rkt takes in four command line arguments the first argument is the file path to the racket file to run mutation testing on, the second arugment is the timeout time in seconds, the third is the output file to store mutation results, and the last is a path to a csv file containing the coverage data for the file to be tested
GIVE EXAMPLE 

I do not reccomend running mutation-tester.rkt alone, instead run the mutate-repos.py file, which will calculate the timeout argument for you. 
Before running mutate-repos.py, run extract_coverage.py to generate the coverage data for each repo.
Once mutate-repos.py is ran, use process-report.py to combine all the json files into a csv.

The above is the main pipeline for generating mutation results for the open-source projects.
