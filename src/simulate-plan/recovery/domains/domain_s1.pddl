(define (domain recovery-blocks)
  (:requirements :strips :typing :equality)
  (:types block surface)

  (:predicates
    (On ?x - block ?y - block)
    (OnTable ?x - block)
    (Clear ?x - block)
    (Holding ?x - block)
    (HandEmpty)
    (TargetOn ?x - block ?y - block)
    (AtTarget ?x - block)
  )

  (:action pickup-from-table
    :parameters (?x - block)
    :precondition (and (HandEmpty) (OnTable ?x) (Clear ?x))
    :effect (and (Holding ?x)
                 (not (OnTable ?x))
                 (not (HandEmpty))
                 (not (AtTarget ?x)))
  )

  (:action putdown-to-table
    :parameters (?x - block)
    :precondition (Holding ?x)
    :effect (and (OnTable ?x) (Clear ?x) (HandEmpty)
                 (not (Holding ?x))
                 (not (AtTarget ?x)))
  )

  (:action unstack
    :parameters (?x - block ?y - block)
    :precondition (and (HandEmpty) (On ?x ?y) (Clear ?x) (not (= ?x ?y)))
    :effect (and (Holding ?x) (Clear ?y)
                 (not (On ?x ?y)) (not (HandEmpty))
                 (not (AtTarget ?x)))
  )

  (:action stack
    :parameters (?x - block ?y - block)
    :precondition (and (Holding ?x) (Clear ?y) (not (= ?x ?y)))
    :effect (and (On ?x ?y) (Clear ?x) (HandEmpty)
                 (not (Holding ?x)) (not (Clear ?y))
                 (not (AtTarget ?x)))
  )

  (:action stack-target
    :parameters (?x - block ?y - block)
    :precondition (and (Holding ?x) (Clear ?y) (TargetOn ?x ?y) (not (= ?x ?y)))
    :effect (and (On ?x ?y) (Clear ?x) (HandEmpty)
                 (not (Holding ?x)) (not (Clear ?y))
                 (AtTarget ?x))
  )
)
