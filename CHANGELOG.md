v1.1.1
======

 * Immediately return if cols is empty.
 
v1.1.0
======

 * Optionally pass drop_invariant to any encoder to consistently drop columns with 0 variance from the output (based on training set data in fit())
 * If None is passed as the cols param, every string column will be encoded (pandas type = object).
 
v1.0.5
======

 * Changed setup.py to not explicitly force reinstalls of other packages
 
v1.0.4
======

 * Bugfixes
 
v1.0.0
======

 * First real usable release, includes sklearn compatible encoders.
 
v0.0.1
======

 * Basic library of encoders, no automated testing.