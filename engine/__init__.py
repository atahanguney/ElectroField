"""ElectroField physics engine.

Every public solver returns plain dicts that are JSON-serialisable and carry:
  * values  - computed quantities with SI units
  * steps   - the derivation, formula -> substitution -> result
  * checks  - independent verifications (alternative formula, limiting case,
              numerical residual of Maxwell's equations, numerical integration)
The UI only renders what this package computes.
"""
