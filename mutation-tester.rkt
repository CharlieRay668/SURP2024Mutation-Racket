#lang at-exp racket

(require syntax/parse
         mutate
         mutate/traversal
         mutate/logger
         "./read-module.rkt"
         csv-reading)

(define (get-source-location stx)
  (let ([source (syntax-source stx)]
        [line (syntax-line stx)]
        [column (syntax-column stx)])
    (format "File: ~a, Line: ~a, Column: ~a" source line column)))

(define (replace-at-index lst index replacement)
  (append (take lst index)
          (list replacement)
          (drop lst (+ index 1))))

(define (remove-at-index lst index)
  (if (= index (sub1 (length lst)))
      (take lst index)
      (append (take lst index) (drop lst (+ index 1)))))

(define (replace-cond-test lst index replacement)
  (append (take lst index)
          (list (let ([clause (list-ref lst index)])
                  (list replacement (second clause))))
          (drop lst (+ index 1))))

(define (generate-removal-stream stx-list stx-ref)
  (let* ([lst (cdr stx-list)]
         [len (length lst)])
    (for/stream ([index (in-range len)])
      ; (printf "Removing index ~a from list of length ~a: ~a\n" index len lst)
      (datum->syntax
       stx-ref
       `(match ,(car stx-list) ,@(remove-at-index lst index))))))

(define (generate-and-replacement-stream stx-list stx-ref replacement)
  (let ([len (length stx-list)])
    (for/stream ([index (in-range len)])
      (datum->syntax
       stx-ref
       `(and ,@(replace-at-index (map syntax-e stx-list) index replacement))))))

(define (generate-or-replacement-stream stx-list stx-ref replacement)
  (let ([len (length stx-list)])
    (for/stream ([index (in-range len)])
      (datum->syntax
       stx-ref
       `(or ,@(replace-at-index (map syntax-e stx-list) index replacement))))))

(define (generate-cond-replacement-stream stx-lst stx-ref replacement)
  (let ([len (length stx-lst)])
    (for/stream ([index (in-range len)])
      (datum->syntax
       stx-ref
       `(cond ,@(replace-cond-test (map syntax-e stx-lst) index replacement))))))


(define stx->mutants
    (build-mutation-engine
    #:mutators
    (define-simple-mutator (aod-add stx)
        #:pattern ({~datum +} arg ...)
        (for/stream ([args (in-list (attribute arg))])
        #`(begin #,@args)))
    (define-simple-mutator (aod-minus stx)
        #:pattern ({~datum -} arg ...)
        (for/stream ([args (in-list (attribute arg))])
        #`(begin #,@args)))
    (define-simple-mutator (aod-mul stx)
        #:pattern ({~datum *} arg ...)
        (for/stream ([args (in-list (attribute arg))])
        #`(begin #,@args)))
    (define-simple-mutator (aod-div stx)
        #:pattern ({~datum /} arg ...)
        (for/stream ([args (in-list (attribute arg))])
        #`(begin #,@args)))
    (define-simple-mutator (aod-mod stx)
        #:pattern ({~datum modulo} arg ...)
        (for/stream ([args (in-list (attribute arg))])
        #`(begin #,@args)))
    (define-simple-mutator (RC-and->false stx)
        #:pattern ({~datum and} fst args ...)
        (generate-and-replacement-stream (syntax->list #'(fst args ...)) #'fst #f))
    (define-simple-mutator (RC-and->true stx)
        #:pattern ({~datum and} fst args ...)
        (generate-and-replacement-stream (syntax->list #'(fst args ...)) #'fst #t))
    (define-simple-mutator (RC-or->false stx)
        #:pattern ({~datum or} fst args ...)
        (generate-or-replacement-stream (syntax->list #'(fst args ...)) #'fst #f))
    (define-simple-mutator (RC-or->true stx)
        #:pattern ({~datum or} fst args ...)
        (generate-or-replacement-stream (syntax->list #'(fst args ...)) #'fst #t))
    (define-simple-mutator (RC-cond->false stx)
        #:pattern ({~datum cond} [tests argses ...] ...)
        (generate-cond-replacement-stream (syntax->list #'([tests argses ...] ...)) #'([tests argses ...] ...) #f))
    (define-simple-mutator (RC-cond->true stx)
        #:pattern ({~datum cond} [tests argses ...] ...)
        (generate-cond-replacement-stream (syntax->list #'([tests argses ...] ...)) #'([tests argses ...] ...) #t))
    (define-simple-mutator (RC-if->false stx)
        #:pattern ({~datum if} test then el)
        #'(if #f then el))
    (define-simple-mutator (RC-if->true stx)
        #:pattern ({~datum if} test then el)
        #'(if #t then el))
    (define-simple-mutator (RC-match-removal stx)
          #:pattern ((~datum match) fst clauses ...)
          (generate-removal-stream (syntax->list #'(fst clauses ...)) #'fst))
   #:syntax-only
   #:top-level-selector select-define-body
   #:streaming
   #:module-mutator))
; (printf "Mutators loaded\n")
(define (get-mutants p)
  (stx->mutants (read-module p)))
; (printf "Mutants generated\n")
(define log-receiver
  (make-log-receiver mutate-logger 'info))

(define filepath
  (vector-ref (current-command-line-arguments) 0))

(define timeout-limit
  (string->number (vector-ref (current-command-line-arguments) 1)))

(define output-file 
  (vector-ref (current-command-line-arguments) 2))

(define csv-file 
  (vector-ref (current-command-line-arguments) 3))

(define out
  (open-output-file output-file #:exists 'replace))

;; Function to read the CSV file and convert it to a list of numbers
(define (read-line-numbers csv-file)
  (define reader (make-csv-reader (open-input-file csv-file)))
  (let loop ((result '()))
    (define row (reader))
    (if (null? row)
        (reverse result)
        (loop (cons (string->number (first row)) result)))))

;; Read the CSV file and store the line numbers in a list
(define line-numbers (read-line-numbers csv-file))

;; Function to test if a number is in the list of line numbers
(define (contains-line? n)
  (not (false? (member n line-numbers))))

(define (extract-mutation-info)
  (let ([log-entry (sync log-receiver)])
    (define third-val (vector-ref log-entry 2))
    (values third-val)))

;; run the given program with the given argument for a maximum of the given number
;; of seconds, return a list containing the two resulting strings for stdout and stderr
;; func copied from JC - CR
(define (subprocess/noinput/timeout timeout-secs prog . args)
  (define-values (the-subprocess sub-stdout sub-stdin sub-stderr)
    (apply
     subprocess #f #f #f 'new
     prog args))
  ;; no need to send input to subprocess, close it now:
  (close-output-port sub-stdin)
  ;; create the timer thread
  (define timer-thread (thread (λ () (sleep timeout-secs) 'timeout)))
  ;; wait for either the timer thread or the subprocess to finish:
  (define sync-result
    (time (sync timer-thread the-subprocess)))
  (when (thread? sync-result)
    (printf "timeout! must kill subprocess\n")
    ;; timeout! kill the subprocess
    (subprocess-kill the-subprocess #f))
  ;; grab the text from the stdout and stderr pipes
  (define stdout-text (first (regexp-match #px".*" sub-stdout)))
  (define stderr-text (first (regexp-match #px".*" sub-stderr)))
  (close-input-port sub-stdout)
  (close-input-port sub-stderr)
  (list stdout-text stderr-text (subprocess-status the-subprocess)))

; (printf "getting total mutants\n")
(define mutants (stream->list(get-mutants filepath)))
; (printf "All the")
(define total-mutants (length mutants))
; (printf "Total mutants: ~a\n" total-mutants)
(define elapsed-time 0)

; (define total-mutants 100)

(define score
  (for/fold ([failure 0]
             [total 0]
             #:result (/ failure total))
            ([mutant-stx (get-mutants filepath)])
    (define temp (make-temporary-file  "mutant-~a"))
    ; Add timing information - CR
    (define start-time (current-inexact-milliseconds))
    (write-to-file (syntax->datum mutant-stx) temp #:exists 'replace)
    ;; the handling of the logger here is weird. All of the
    ;; messages (events) in this queue are already queued before
    ;; the loop starts, generated by get-mutants. This code
    ;; pulls them out one at a time, and I believe they will
    ;; have to come out in the right order. I'm kind of not a fan
    ;; of this way of writing the code. Indeed, it seems a bit
    ;; weird to use a logger here at all.
    (match (sync log-receiver)
      [(vector level message (list type from-stx to-stx) logger-topic)
        
        ; (printf "Is syntax ~a\n" (syntax-source from-stx))
        ;; print out the message:
        ; I write to a file and then use python to parse the strings into JSON,
        ; It's not smart, in any way - CR
        (write (format "/#:NUM MUTANT: ~a:#/" total) out)
        (write (format "/#:MUTANT USED: ~a:#/" type) out)
        (write (format "/#:MUTANT SOURCE FILE: ~a:#/" (syntax-source from-stx)) out)
        (write (format "/#:MUTANT SOURCE LINE: ~a:#/" (syntax-line from-stx)) out)
        (write (format "/#:MUTANT SOURCE COLUMN: ~a:#/" (syntax-column from-stx)) out)
        (write (format "/#:MUTANT SOURCE: ~a:#/" (syntax->datum from-stx)) out)
        (write (format "/#:MUTANT DESTINATION: ~a:#/" (syntax->datum to-stx)) out)
        ; Tests if the tests-pass
        (define covered? (contains-line? (syntax-line from-stx)))
        (cond [(not covered?)
              (write "MUTANT_RESULT: not_covered//##::##//" out)
              (values failure (add1 total))]
              [else
                (match-define (list stdout-text stderr-text tests-pass?)
                (time (subprocess/noinput/timeout timeout-limit (find-executable-path "raco") "test" temp)))
                (delete-file temp)
                (cond
                      [(equal? tests-pass? 0)
                      (write "MUTANT_RESULT: survived//##::##//" out)]
                      [else
                      (write "MUTANT_RESULT: killed//##::##//" out)])
                (values (+ failure (if (equal? tests-pass? 0) 0 1))
                      (add1 total))])]
      [other
        (printf "unexpected log message: ~e\n" other)
        (error 'message "unexpected log message: ~e" other)])))
    

(write (~a "\n\n\nMutation score: " (~r score)) out)
; (printf "Mutation score: ~a\n" score)
(close-output-port out)