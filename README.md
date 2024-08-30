# Mutation Analysis Pipeline for Racket Projects

The code in this repository has an extraordinary amount of technical debt. I apologize in advance. This repo is essentially a collection of scripts (Bash or Python) that all work together to build a pipeline for Mutation analysis on Racket projects.

## Main Files

### `mutation-tester.rkt`
This is the primary file that actually runs mutation analysis. The following mutators are defined within this file:

- **aod-add (Arithmetic Deletion Operator, Addition)**
  - Mutates `(+ 1 2 3)` into three mutants: `1`, `2`, or `3`.
  - Mutates `(+ j_1 j_2 ... j_n)` into `n` mutants: `j_i` for all `1 <= i <= n`.

- **aod-minus (Arithmetic Deletion Operator, Subtraction)**
  - Mutates `(- 1 2 3)` into three mutants: `1`, `2`, or `3`.
  - Mutates `(- j_1 j_2 ... j_n)` into `n` mutants: `j_i` for all `1 <= i <= n`.

- **aod-mul (Arithmetic Deletion Operator, Multiplication)**
  - Mutates `(* 1 2 3)` into three mutants: `1`, `2`, or `3`.
  - Mutates `(* j_1 j_2 ... j_n)` into `n` mutants: `j_i` for all `1 <= i <= n`.

- **aod-div (Arithmetic Deletion Operator, Division)**
  - Mutates `(/ 1 2 3)` into three mutants: `1`, `2`, or `3`.
  - Mutates `(/ j_1 j_2 ... j_n)` into `n` mutants: `j_i` for all `1 <= i <= n`.

- **aod-mod (Arithmetic Deletion Operator, Modulo)**
  - Mutates `(modulo 1 2 3)` into three mutants: `1`, `2`, or `3`.
  - Mutates `(modulo j_1 j_2 ... j_n)` into `n` mutants: `j_i` for all `1 <= i <= n`.

- **RC-and->false (Remove Conditionals, insert false into and)**
  - Mutates `(and x y z)` into three mutants: `(and #f y z)`, `(and x #f z)`, and `(and x y #f)`.
  - Mutates `(and j_1 j_2 ... j_n)` into `n` mutants where one `j_i` is replaced with `#f`.

- **RC-and->true (Remove Conditionals, insert true into and)**
  - Mutates `(and x y z)` into three mutants: `(and #t y z)`, `(and x #t z)`, and `(and x y #t)`.
  - Mutates `(and j_1 j_2 ... j_n)` into `n` mutants where one `j_i` is replaced with `#t`.

- **RC-or->false (Remove Conditionals, insert false into or)**
  - Mutates `(or x y z)` into three mutants: `(or #f y z)`, `(or x #f z)`, and `(or x y #f)`.
  - Mutates `(or j_1 j_2 ... j_n)` into `n` mutants where one `j_i` is replaced with `#f`.

- **RC-or->true (Remove Conditionals, insert true into or)**
  - Mutates `(or x y z)` into three mutants: `(or #t y z)`, `(or x #t z)`, and `(or x y #t)`.
  - Mutates `(or j_1 j_2 ... j_n)` into `n` mutants where one `j_i` is replaced with `#t`.

- **RC-cond->false (Remove Conditionals, insert false into cond)**
  - Mutates `(cond [x 3] [y 3] [else 4])` into three mutants: `(cond [#f 3] [y 3] [else 4])`, `(cond [x 3] [#f 3] [else 4])`, and `(cond [x 3] [y 3] [#f 4])`.
  - Mutates `(cond [j_1 foo] ... [j_n foo])` into `n` mutants where one `j_i` is replaced with `#f`.

- **RC-cond->true (Remove Conditionals, insert true into cond)**
  - Mutates `(cond [x 3] [y 3] [else 4])` into three mutants: `(cond [#t 3] [y 3] [else 4])`, `(cond [x 3] [#t 3] [else 4])`, and `(cond [x 3] [y 3] [#t 4])`.
  - Mutates `(cond [j_1 foo] ... [j_n foo])` into `n` mutants where one `j_i` is replaced with `#t`.

- **RC-if->false (Remove Conditionals, force else branch)**
  - Mutates `(if cond then else)` into one mutant: just the `else` branch.

- **RC-if->true (Remove Conditionals, force then branch)**
  - Mutates `(if cond then else)` into one mutant: just the `then` branch.

- **RC-match-removal (Remove Conditionals, remove one match branch)**
  - Mutates `(match [cond_1 then] [cond_2 then] [cond_3 then])` into three mutants: 
    - `(match [cond_2 then] [cond_3 then])`
    - `(match [cond_1 then] [cond_3 then])`
    - `(match [cond_1 then] [cond_2 then])`
  - Mutates `(match [cond_1 then] ... [cond_n then])` into `n` mutants where one `cond_i` branch is removed.

### Running Mutation Tests

`mutation-tester.rkt` takes in four command line arguments:
1. The file path to the Racket file to run mutation testing on.
2. The timeout time in seconds.
3. The output file to store mutation results.
4. A path to a CSV file containing the coverage data for the file to be tested.

**Example:**
```bash
racket mutation-tester.rkt yourfile.rkt 60 output.json coverage.csv
```

### Recommended Usage
I do not recommend running `mutation-tester.rkt` alone. Instead, run the `mutate-repos.py` file, which will calculate the timeout argument for you. 

1. **Before running `mutate-repos.py`,** run `extract_coverage.py` to generate the coverage data for each repo.
2. Once `mutate-repos.py` is run, use `process-report.py` to combine all the JSON files into a CSV.

This is the main pipeline for generating mutation results for the open-source projects.

### CSC480 Projects
To mutate the CSC480 projects, use `mutation-tester-assignments.rkt`. It is nearly identical to `mutation-tester.rkt`, but it doesn't use coverage data. Additionally, use `mutate-assignments.py` to run `mutation-tester-assignments.rkt`.

### Running MACKET
To run MACKET on the open-source projects, run:
```bash
python run_macket_on_repos.py
```

You must install MACKET; see (https://github.com/neu-se/MACKET)

## Notes
- I mark "timed out" mutants as killed since the tests did not pass.
- `mutation-tester-assignments` only has Survived and Killed mutants since it doesn't have coverage data to generate "Not-covered" mutants.
- As mentioned, this code has significant technical debt. Realistically, most of the Python files could be removed, and `mutate-repos.rkt` could build CSV files on its own, along with processing coverage data and estimating time-out requirements.

